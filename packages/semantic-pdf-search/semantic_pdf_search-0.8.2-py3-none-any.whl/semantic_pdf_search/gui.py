import customtkinter as ctk
import tkinter as tk
from typing import Optional
import os
import shutil
from pathlib import Path
import webbrowser
import pymupdf
from threading import Thread
import pickle

PDFS_DIR = Path(__file__).parent / Path("pdfs")




import socket

def is_connected(timeout=1):
    """
    If internet is not connected, set HF_HUB_OFFLINE=1. This prevents infinite loading time when offline.
    """
    test_hosts = [
        ("1.1.1.1", 53),          # Cloudflare
        ("8.8.8.8", 53),          # Google
        ("9.9.9.9", 53),          # Quad9
        ("208.67.222.222", 53),   # OpenDNS
    ]
    for host, port in test_hosts:
        try:
            socket.setdefaulttimeout(timeout)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((host, port))
                return True
        except socket.error:
            continue
    return False



 
class SemanticSearchGUI:
    """
    This class contains all the necessary methods to present a working GUI to the user.
    """
    def __init__(self):
        """
        Attempt to load the state file and otherwise give the instructional message. Load the filenames of previously
          embedded PDFs, present the main window to the user, start a thread to load the sentence-encoders module.
        """
        self.menubar = None
        self.current_pdf_path = None
        self.can_scroll = False
        self.factory_reset_confirmation = None
        self.state = self.load_state()

        self.pdfs = self.get_recent_pdfs()

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.main_window=ctk.CTk()
        self.main_window.protocol("WM_DELETE_WINDOW", self.save_state_and_close)
        self.main_window.geometry("800x600")
        self.import_thread:Thread=Thread(target = self.import_from_main)
        self.import_thread.start()
        self.query_frame = ctk.CTkFrame(self.main_window)
        self.queries_results_frame=ctk.CTkScrollableFrame(self.main_window)
        self.main_window.bind("<Configure>",self.update_should_scroll)
        if self.is_first_run == True:   
            self.fresh_start()
            self.queries_results_frame.pack(fill='both',expand=True)
        
        self.populate_file_dialogue()

    def import_from_main(self)->None:
        """
        Import the Searcher and SentenceEncoder class from main. This also loads the sentence-encoders module which can take some time. 
        """
        global Searcher,SentenceEncoder
        from semantic_pdf_search.main import Searcher,SentenceEncoder

    def get_stored_pdfs(self) -> list[str]: 
        """
        Return a list of stored (previously embedded) PDFs by filename.
        """
        if not os.path.isdir(PDFS_DIR):
            os.mkdir(PDFS_DIR)
        return [str(child) for child in PDFS_DIR.iterdir()]
        
    def get_recent_pdfs(self) -> list[str]:
        """
        Return a list of recently opened PDFs by filename.
        """
        files_times = []

        if not os.path.isdir(PDFS_DIR):
            os.mkdir(PDFS_DIR)

        for child in PDFS_DIR.iterdir():
            if child.is_file():
                try:
                    files_times.append((str(child),os.path.getmtime(child)))
                except Exception as e:
                    continue
        files_times.sort(key=lambda x: x[1], reverse=True)
        return [file for file, _ in files_times[:10]]

        
    def populate_file_dialogue(self) -> None:
        """
        Populates the file dialogue. This includes buttons to load previously embedded PDFs and one to embed a new PDF from a file dialogue.
        """
        if self.menubar is not None: 
            self.pdfs = self.get_recent_pdfs()
            browse_button_index=self.pdf_menu.index('end')
            if not browse_button_index:
                browse_button_index = 0

            for i in range(browse_button_index):
                self.pdf_menu.delete(0)

            for path in reversed(self.pdfs):
                name = Path(path).name
                self.pdf_menu.insert_command(0,label=name, command=lambda path=path: self.load_pdf(path))
            
        else:
            self.menubar=tk.Menu(self.main_window)
            submenu=tk.Menu(self.menubar,tearoff=0)
            self.main_window.config(menu=self.menubar)
            self.menubar.add_cascade(label="File ...",menu=submenu)
            self.pdf_menu = tk.Menu(self.menubar, tearoff=0)
            settings_menu = tk.Menu(self.menubar, tearoff=0)

            submenu.add_cascade(label="Open ...", menu=self.pdf_menu)
            for path in self.pdfs:
                    name = Path(path).name
                    self.pdf_menu.add_command(label=name, command=lambda path=path: self.load_pdf(path))
            self.pdf_menu.add_command(label="Browse for PDF", command=self.browse_for_pdf)        

            submenu.add_separator()    

            submenu.add_cascade(label="Settings", menu=settings_menu)
            
            settings_menu.add_command(label="Factory Reset", command=self.spawn_reset_window)
            
            submenu.add_command(label="Quit", command=self.save_state_and_close)
            
            self.menubar.add_command(label="")
            
           
           
            
        
    
    def get_previous_queries(self, pdf_path: str) -> None:
        """
        Load previous queries from state and display results to user.
        """
        if self.state != None and pdf_path in self.state: 

            self.queries_results_frame.columnconfigure(1,weight=1)
            
            for i,query in enumerate(self.state[pdf_path]):
                #add new row to grid here
                self.queries_results_frame.rowconfigure(i,weight=1)
                #add query as Label here
                query_label = ctk.CTkLabel(self.queries_results_frame, text=query)        
                query_label.grid(column=0, row=i, sticky=ctk.EW, padx=10, pady=10)
                query_results=ctk.CTkFrame(self.queries_results_frame)
                query_results.grid(column=1, row=i, sticky=ctk.EW, padx=10, pady=10)
                for i, result in enumerate(self.state[pdf_path][query]):
                    #add result as button 
                    query_results.columnconfigure(i,weight=1)
                    query_result = ctk.CTkButton(query_results,text=str(result), command = lambda pdf_path=pdf_path,result=result: self.open_pdf(pdf_path, result))
                    query_result.grid(column=i, row=0, sticky=ctk.EW)
                query_results.columnconfigure(len(self.state[pdf_path][query]),weight=1)
                delete_query_button=ctk.CTkButton(query_results,text="Remove",command=lambda query=query: self.remove_query_result(query=query))
                delete_query_button.grid(column=len(self.state[pdf_path][query]), row=0, sticky=ctk.EW)

            self.queries_results_frame.pack(fill='both',expand=True)  

    def scroll_results_frame(self, event):
        """Scroll the frame when the mouse wheel is used."""
        if event.num == 4:
            self.queries_results_frame._parent_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.queries_results_frame._parent_canvas.yview_scroll(1, "units")
        else:
            self.queries_results_frame._parent_canvas.yview_scroll(int(-1*(event.delta/120)), "units")


    def remove_query_result(self,query:str)->None:
        """
        Removes a query and its result from the list.
        """
        if self.state != None:
            if self.current_pdf_path in self.state:
                if query in self.state[self.current_pdf_path]:
                    del self.state[self.current_pdf_path][query]
        target_row = None
        for widget in self.queries_results_frame.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                if widget.cget('text') == query:
                    target_row = widget.grid_info()['row']
        should_stick_to_bottom = False
        if self.queries_results_frame._parent_canvas.yview()[1] == 1.0:
            should_stick_to_bottom = True        
        for widget in self.queries_results_frame.grid_slaves(row=target_row):
            widget.destroy()
        if should_stick_to_bottom:
            self.queries_results_frame._parent_canvas.yview_moveto(1.0)
        self.main_window.update()
        self.update_should_scroll()

    def load_pdf(self,pdf_path:str)-> None:
        """
        Load a known PDF and display previous queries. Also sets the window title. 
        Loading a PDF can take a while even if the embedding file exists because of the import time for the sentence-transformers package
        and the time taken to run torch.load(). Note that a PDF being 'known' only means that the PDF file is in the `pdfs` folder. 
        
        Originally there were supposed to be two functions depending on if the embedding file existed for that PDF but they would be 
        largely identical because the call to ``Searcher.forPDF()`` handles this case internally. 
        """
        for widget in self.queries_results_frame.winfo_children():
            widget.destroy()

        self.query_frame.destroy()
        
        progress_bar= ctk.CTkProgressBar(self.main_window,mode="determinate")
        progress_bar.pack(side=ctk.BOTTOM,padx=20,pady=20,fill='x',anchor='center')
        progress_text= ctk.CTkLabel(self.main_window,text="Importing Libraries")
        progress_text.pack(side=ctk.BOTTOM)
        progress_bar.set(.05)
        self.main_window.update()
        if self.import_thread.is_alive():
            self.import_thread.join()

        MODEL = SentenceEncoder.MODEL1
        progress_bar.set(.20)
        self.main_window.update()
        self.current_pdf_path=pdf_path
        progress_text.configure(text="Loading Previous Queries")
        progress_bar.set(.25)
        self.main_window.update()
        self.get_previous_queries(pdf_path)
        progress_bar.set(.35)
        progress_text.configure(text="Loading Embeddings")
        self.main_window.update()
        self.searcher = Searcher.forPDF(
        SentenceEncoder(
            MODEL),pdf_path, str(Path(__file__).parent / Path("embeddings")))
        progress_bar.set(.75)
        progress_text.configure(text="Finalizing")
        
        self.main_window.update()
        self.main_window.title(f"Semantic search: {Path(pdf_path).name}")
        self.menubar.delete(2)
        self.menubar.insert_command(2,label=f"Current PDF: {Path(pdf_path).name}")
        progress_bar.destroy()
        self.show_search_bar()
        progress_text.destroy()
        ...
    def browse_for_pdf(self)-> None:
        """
        This function opens the file dialog and allows the user to select a PDF. The selected
        PDF will get hashed and if the hash does not match any known hash, the PDF will get copied into 
        the `pdfs` directory and the embeddings will be created.
        """
        
        filepath = ctk.filedialog.askopenfilename(title='Select a PDF', initialdir=PDFS_DIR, filetypes=(('PDF', '*.pdf'), ))
        from semantic_pdf_search.main import Corpus,Constants
        MODEL = Constants.MODEL1
        EMBEDDINGS_DIR = Path(__file__).parent / Path("embeddings") / Path(f"Encoder: {MODEL}")
        if not os.path.isdir(EMBEDDINGS_DIR.parent):
            os.mkdir(EMBEDDINGS_DIR.parent)
        if not os.path.isdir(EMBEDDINGS_DIR):
            os.mkdir(EMBEDDINGS_DIR)
        if filepath:
            reader = pymupdf.open(filepath)
            pages = [reader.load_page(i) for i in range(len(reader))]
            corpus = Corpus([page.get_text() for page in pages])
            embedding = EMBEDDINGS_DIR / Path(str(hash(corpus)))
            embedding_names = [path.name for path in EMBEDDINGS_DIR.iterdir()]
            if embedding.name not in embedding_names:
                pdf_names = [pdf.name for pdf in PDFS_DIR.iterdir()]
                if(Path(filepath).name not in pdf_names):
                    shutil.copy(filepath,PDFS_DIR)
                    self.load_pdf(str(PDFS_DIR / Path(filepath).name))
                else:
                    new_path = PDFS_DIR / f"_{Path(filepath).name}"
                    shutil.copy(filepath,new_path)
                    self.load_pdf(str(new_path))
                self.populate_file_dialogue()
            else:
                self.load_pdf(filepath)
            reader.close()


    def open_pdf(self, pdf_path: str, page : int)-> None:
        """
        TODO: handle mac opening pdfs in webbrowser by using local server to host the PDF 
        """
        webbrowser.open(f"file://{pdf_path}#page={page}")

    def fresh_start(self)-> None:
        """
        User opens app, told to select File ... -> Browse for PDF
        """
        intro = ctk.CTkLabel(self.queries_results_frame, text="To start a search, first select a PDF. \n " \
        "Click on File ... -> Open ... -> Browse for PDF.", font=ctk.CTkFont(size=20, weight="bold"))
        
        intro.grid(column=1,row=1)
        
        ...

    
    def show_search_bar(self)->None:
        """
        A new frame is shown and the user is given a button which, 
        when pressed, presents an entry field for the user to enter a search query. 
        """
        self.query_frame = ctk.CTkFrame(self.main_window)
        self.query_frame.pack(side=tk.BOTTOM,pady=50)
        entry_text=tk.StringVar()
        query_entry_field = ctk.CTkEntry(self.query_frame,textvariable=entry_text)
        query_entry_instructions = ctk.CTkLabel(self.query_frame,text="Enter query:")
        query_entry_instructions.pack(side=tk.LEFT,padx=20)
        query_entry_field.bind("<Return>", lambda event: self.handle_enter_query(entry_text.get()))
        query_entry_field.pack(side=tk.BOTTOM)

    def handle_enter_query(self, entry:str )->None:
        """
        The query is searched for and the results are displayed to the user. The results are also stored to the state.
        """
        if self.state != None:
            if self.current_pdf_path not in self.state:
                self.state[self.current_pdf_path]={entry:self.searcher(entry,top_k=5)}
                self.queries_results_frame.columnconfigure(1,weight=1)
            elif entry not in self.state[self.current_pdf_path]:
                self.state[self.current_pdf_path][entry]=self.searcher(entry,top_k=5)
                self.queries_results_frame.columnconfigure(1,weight=1)
            else:
                return
            [ _ , num_rows ] = self.queries_results_frame.grid_size()
            should_stick_to_bottom = False
            if self.queries_results_frame._parent_canvas.yview()[1] == 1.0:
                should_stick_to_bottom = True
            self.queries_results_frame.rowconfigure(num_rows,weight=1)
            #add query as Label here
            query_label = ctk.CTkLabel(self.queries_results_frame, text=entry)        
            query_label.grid(column=0, row=num_rows, sticky=ctk.EW, padx=10, pady=10)
            query_results=ctk.CTkFrame(self.queries_results_frame)
            query_results.grid(column=1, row=num_rows, sticky=ctk.EW, padx=10, pady=10)
            for i, result in enumerate(self.state[self.current_pdf_path][entry]):
                #add result as button 
                query_results.columnconfigure(i, weight=1)
                query_result = ctk.CTkButton(query_results,text=str(result), command = lambda pdf_path=self.current_pdf_path,result=result: self.open_pdf(pdf_path, result))
                query_result.grid(column=i, row=0, sticky=ctk.EW)
            query_results.columnconfigure(len(self.state[self.current_pdf_path][entry]), weight=1)
            delete_query_button=ctk.CTkButton(query_results,text="Remove",command=lambda query=entry: self.remove_query_result(query=query))
            delete_query_button.grid(column=len(self.state[self.current_pdf_path][entry]), row=0, sticky=ctk.EW)
            if should_stick_to_bottom:
                self.queries_results_frame._parent_canvas.yview_moveto(1.0)
            self.queries_results_frame.pack(fill='both',expand=True)
            
            self.main_window.update()
            self.update_should_scroll()
                    
                    


    def update_should_scroll(self, event = None)->None:
        if self.queries_results_frame != None and self.current_pdf_path != None:
            canvas = self.queries_results_frame._parent_canvas

            # Wrap entry label text to 20% of current window size
            window_width = self.main_window.winfo_width()
            wraplength_value = int(window_width * 0.20)

            for widget in self.queries_results_frame.winfo_children():
                if isinstance(widget, ctk.CTkLabel):
                    widget.configure(wraplength=wraplength_value)
            if canvas.cget("scrollregion"):
                scroll_region = canvas.cget("scrollregion").split()
                full_height = float(scroll_region[3]) - float(scroll_region[1])
                visible_height = canvas.winfo_height()
                if full_height > visible_height:
                    if self.can_scroll == False:
                        #Enable scroll binding
                        #windows
                        self.queries_results_frame.bind_all("<MouseWheel>", self.scroll_results_frame)
                        #linux
                        self.queries_results_frame.bind_all("<Button-4>", self.scroll_results_frame)  
                        self.queries_results_frame.bind_all("<Button-5>", self.scroll_results_frame)  
                        self.can_scroll = True
                else:            
                    if self.can_scroll == True:
                        #Enable scroll binding
                        #windows
                        self.queries_results_frame.unbind_all("<MouseWheel>")
                        #linux
                        self.queries_results_frame.unbind_all("<Button-4>")  
                        self.queries_results_frame.unbind_all("<Button-5>")  
                        self.can_scroll = False

    def display_results(self,query:str, results: list[int])->None:
        """
        Once all pages have been searched and the top 5 results have been found, 
        the pages will be shown to the user as a horizontal row of buttons labeled 
        with the resulting page numbers.         
        """
        #add new row to grid here
        self.queries_results_frame.rowconfigure(0,weight=1)
        self.queries_results_frame.columnconfigure(1, weight=3)
        #add query as Label here
        
        query_label = ctk.CTkLabel(self.queries_results_frame, text=query)        
        query_label.grid(column=0, row=0, sticky=tk.EW, padx=10, pady=10)
        query_results=ctk.CTkFrame(self.queries_results_frame)
        query_results.grid(column=1, row=0, sticky=tk.EW, padx=10, pady=10)

        for result in results:
            #add result as button 
            query_result = ctk.CTkButton(query_results,text=str(result), command = lambda result=result: self.open_pdf(self.current_pdf_path, result), style='Accent.TCTkButton', padding=0)
            query_result.pack(side=tk.RIGHT)
        delete_query_button=ctk.CTkButton(query_results,text="Remove",command=lambda query=query: self.remove_query_result(query=query))
        delete_query_button.pack(side=tk.LEFT)
        self.queries_results_frame.pack(fill='both',expand=True)

    def save_state_and_close(self)-> None:
        """
        The query, the PDF hash, and all the results are stored to a 
        pickle dictionary file. 
        """
        directory=Path(__file__).parent
        file=Path("state.pck")
        with open(directory / file, "wb") as f:
            pickle.dump(file=f,obj=self.state)
        self.main_window.destroy()
    def load_state(self) -> Optional[dict[str, dict[str, list[int]]]]:
        """
        Loads state from pickle file and returns a dictionary representation. If there is no saved state, 
        returns None.
        """
        state:dict[str,dict[str,list[int]]];

        directory=Path(__file__).parent
        file=Path("state.pck")
        
        if f"{file}" in os.listdir(directory):
            with open(directory / file, "rb") as f:
                state=pickle.load(file=f)
            self.is_first_run = False
        else:
            state=dict[str,dict[str,list[int]]]()
            self.is_first_run = True

        return state
    def spawn_reset_window(self)-> None:
        """
        Deletes all stored PDFs and embeddings. Also deletes the state file if it exists.
        """
        if self.factory_reset_confirmation is not None:
            return
        self.factory_reset_confirmation = ctk.CTkToplevel(self.main_window)
        self.factory_reset_confirmation.title("Confirm Factory Reset")
        
        label = ctk.CTkLabel(self.factory_reset_confirmation, text="Are you sure you want to factory reset? This will delete all stored PDFs and embeddings.", wraplength=300)
        label.pack(pady=20)
        button_frame = ctk.CTkFrame(self.factory_reset_confirmation)
        button_frame.pack(pady=10)
        yes_button = ctk.CTkButton(button_frame, text="Yes", command= self.perform_factory_reset)
        yes_button.pack(side=ctk.LEFT, padx=10)
        no_button = ctk.CTkButton(button_frame, text="No", command=self.cancel_factory_reset)
        no_button.pack(side=ctk.LEFT, padx=10)
        self.factory_reset_confirmation.protocol("WM_DELETE_WINDOW", self.cancel_factory_reset) 
    def cancel_factory_reset(self)-> None:
        """ 
        Cancels the factory reset operation and closes the confirmation dialog.
        """
        if self.factory_reset_confirmation is not None:
            self.factory_reset_confirmation.destroy()
            self.factory_reset_confirmation = None
    def perform_factory_reset(self)-> None:
        """
        Performs the factory reset by deleting all stored PDFs, embeddings, and the state file.
        Then, it reinitializes the GUI.
        """
        root_dir=Path(__file__).parent  
        pdf_dir = root_dir / Path("pdfs")
        if os.path.isdir(pdf_dir):
            shutil.rmtree(pdf_dir)
        embeddings_dir = root_dir / Path("embeddings")
        if os.path.isdir(embeddings_dir):
            shutil.rmtree(embeddings_dir)
        
        file=Path("state.pck")
        if f"{file}" in os.listdir(root_dir):
            os.remove(root_dir / file)
        self.main_window.destroy()
        self.__init__()
        self.main_window.mainloop()
def main():
    if not is_connected():
        os.environ["HF_HUB_OFFLINE"] = "1"
    gui = SemanticSearchGUI()
    gui.main_window.mainloop()