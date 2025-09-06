import random
from math import *
from torch import Tensor
import torch
from sentence_transformers import SentenceTransformer, CrossEncoder
from abc import ABC
import pymupdf
from typing import Optional
import os
import logging
from threading import Thread
#from bert import *

THREADS = os.cpu_count()

logger = logging.getLogger("pypdf")
logger.setLevel(logging.NOTSET)


def get_ranks(scores : Tensor, top_k : Optional[int] = None) -> list[int]:
    """
    Sort the incoming tensor of page scores and then return the top k page numbers.
    """
    ret = torch.sort(scores, descending=True)[1][:top_k].tolist()
    return [r+1 for r in ret]
class AbstractModel(ABC):
    """
    Abstract base class for models.
    """
    def __call__(self, text : str) -> Tensor: ...

    def encoder_name(self) -> str:
        return self.__str__()

    def can_rerank(self) -> bool:
        return False

    def rerank(self, query : str, unordered_texts : list[str], current_scores : Tensor, rerank_count : int) -> list[int]:
        raise NotImplementedError("Not implemented")

class Constants():
    """
    Isolated list of constants for model selection
    """
    MODEL1 = "all-MiniLM-L6-v2" # seems good
    MODEL2 = "all-mpnet-base-v2" # too slow, bad performance
class SentenceEncoder(AbstractModel):
    """
    Sentence Encoder base class.
    """
    MODEL1 = "all-MiniLM-L6-v2" # seems good
    MODEL2 = "all-mpnet-base-v2" # too slow, bad performance

    def __init__(self, model_name : str) -> None:
        self.name = model_name
        self.model = SentenceTransformer(model_name)
        #self.model = load_checkpoint("model.pth")

    def __str__(self) -> str:
        return "Encoder: " + self.name

    def __call__(self, text : str) -> Tensor:
        return self.model.encode(text, convert_to_tensor=True)


class RerankingEncoder(SentenceEncoder):
    """
    Reranking Encoder class. 

    This class contains the necessary functions to rerank a list of ranked pages using a reranking cross encoder model.
    """
    MODEL1 = "cross-encoder/ms-marco-TinyBERT-L2-v2"

    def __init__(self, embedder_name : str, reranker_name : str) -> None:
        super().__init__(embedder_name)
        self.reranker_name = reranker_name
        self.reranker_model = CrossEncoder(reranker_name)

    def __str__(self):
        return f"Reranking: {self.reranker_name}/{self.name}"

    def encoder_name(self) -> str:
        return super().__str__()

    def can_rerank(self) -> bool:
        return True
    
    def rerank(self, query : str, unordered_texts: list[str], current_scores : Tensor, rerank_count : int) -> list[int]:
        """
            This function takes the ranked pages from a Searcher and reranks them, returning the ordered list of page ranks.
        """
        ranks = get_ranks(current_scores, top_k = None)
        ordered_texts = [unordered_texts[r] for r in ranks]
        ordered_ranks = [r for r in ranks]
        arg_list = [(query, text) for text in ordered_texts[:rerank_count]]
        res = self.reranker_model.predict(arg_list, convert_to_tensor=True)
        max_val = torch.min(res) - 0.001
        min_val = max_val - 10
        steps = len(unordered_texts) - rerank_count
        res = torch.cat([res, torch.linspace(max_val, min_val, steps, device = res.device)])
        return [ordered_ranks[r] +1 for r in get_ranks(res)]


def hash_str(text : str):
    """
    Simple deterministic hash function.
    """
    h = 5381
    r = 0xFFFFFFFFFFFFFFFF
    for c in text:
        h = ((h << 5) + h + ord(c)) & r
    return h

class Corpus:
    """
    This class contains all the necessary functions to store and retrieve PDF page texts.
    """
    def __init__(self, texts : list[str]):
        self.texts = texts

    def __hash__(self) -> int:
        out = 1594430266020640378
        for text in self.texts:
            out ^= hash_str(text)
        return out
    

class Searcher:
    """
    This class contains all the necessary methods to search for a query in a PDF. 
    """

    def __init__(self, 
                 model : AbstractModel,
                 corpus : Corpus,
                 embeddings_dir : str = "embeddings"):        
        self.model = model
        self.corpus = corpus
        self.encodings = self.__load_embeddings(embeddings_dir)

    def __encode_corpus(self):
        """
        Performs vector embedding on all texts in a corpus and return the result.
        """
        return torch.stack([self.model(text) for text in self.corpus.texts], dim = 1)

    def __load_embeddings(self, embeddings_dir : str) -> Tensor:
        """
        Check if PDF has already been embedded. If so, load the embedding from the file and return it, otherwise create an embedding file for this PDF
        and then encodes all text in the corpus and saves the result to the embedding file, finally returning the embedding.
        """
        if not os.path.exists(embeddings_dir):
            os.mkdir(embeddings_dir)
        dir = f"{embeddings_dir}/{self.model.encoder_name()}"
        if self.model.encoder_name() not in os.listdir(embeddings_dir):
            os.mkdir(dir)
        corpus_hash = hash(self.corpus)
        file_path = f"{dir}/{corpus_hash}"
        if f"{corpus_hash}" in os.listdir(dir):
            with open(file_path, "rb") as f:
                return torch.load(f)
        else:
            enc = self.__encode_corpus()
            with open(file_path, "wb") as f:
                torch.save(enc, f) 
            return enc

    @staticmethod
    def __read_pages(page_list : list[pymupdf.Page], out_list : list[str]):
        """
        Extract the text from each page and append it to the ``out_list`` reference list.
        """
        for page in page_list:
            out_list.append(page.get_text())

    @staticmethod
    def forPDF(model : AbstractModel, pdf_path : str, embeddings_dir : str) -> "Searcher":
        """
        Open the PDF and encode the text using the specified model. Threaded.
        """
        if THREADS:
            reader = pymupdf.open(pdf_path)
            pages = [reader.load_page(i) for i in range(len(reader))]
            page_lists = []
            num_pages = len(pages)


            if num_pages>THREADS:
                batch_size = num_pages // THREADS 
            else:
                batch_size = num_pages

            i = 0
            end_page = num_pages #batch_size*(num_pages // batch_size)
            for i in range(0,end_page, batch_size):
                page_lists.append(pages[i:(i+batch_size)])
            #page_lists.append(pages[i:])
            threads : list[Thread] = []
            out_str_lists = [[] for _ in range(len(page_lists))]
            for i in range(len(page_lists)):
                threads.append(Thread(target = Searcher.__read_pages, args = (page_lists[i], out_str_lists[i])))
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            texts : list[str] = []
            for out_strs in out_str_lists:
                texts.extend(out_strs)
            reader.close()
            return Searcher(model, Corpus(texts), embeddings_dir)
    

    
    def __call__(self, query : str, top_k : Optional[int] = 1) -> list[int]:
        """
        Searches for ``query`` in the corpus, returns the results index
        """

        with torch.no_grad():
            query_enc = torch.stack([self.model(query)] * self.encodings.shape[1], dim = 1)
            similarities = torch.cosine_similarity(query_enc, self.encodings, dim = 0)
            if self.model.can_rerank():
                return self.model.rerank(query, self.corpus.texts, similarities, 20)
            else:
                return get_ranks(similarities,top_k)
        

