<h1 align="center"><b>
	semantic-pdf-search
</b></h1>

<h4 align="center"><b>
A semantic PDF searching application, written in Python.
</b></h4>

<p align="center">
By Jordan Zedeck and Jonathan Louis
</p>


## Overview

This application utilizes a machine learning embedding model to encode both a PDF document and a user's queries. This process enables the application to find near-matches to the query within the document, much like an internet search engine would for web-pages. The page number results are displayed as buttons which can be clicked to open the PDF directly to the page in your default web browser.

## Features

  * **Semantic Search:** Finds near-matches and related concepts, not just exact keywords.
  * **Offline Operability:** Once semantic-pdf-search is installed and used once, it can be used completely offline.
  * **Cross-Platform:** Supports Linux, Windows and macOS.

## Example

**Query:** 

![alt text](assets/great-gatsby-search.png)

**Result:**

![alt text](assets/great-gatsby-result.png)

## Installation

### Prerequisites

This package requires **Tkinter**. If you run the command `python -m tkinter` and a new window does not appear, you will need to install it manually.

  * **Windows:** Re-run the [Python installer](https://www.python.org/downloads/windows/) and ensure the **tcl/tk** checkbox is ticked.
  * **macOS:** Install Tkinter using Homebrew with the following command:
    ```
    brew install python-tk
    ```
  * **Linux:** Varies depending on package manager:
  	* **Debian:**
	    ```
	    sudo apt install python3-tk
	    ```
	* **Fedora:**
	    ```
	    sudo dnf install python3-tkinter
	    ```
	* **Arch:** (note that pip installing packages on Arch requires using a venv):
	    ```
	    sudo pacman -S tk
	    ```

### From PyPI

The easiest way to install the package is using `pip`.

```
pip install semantic-pdf-search
```

### From Source

To install from the GitHub repository, follow these steps:

```
cd semantic-pdf-search
python -m build
pip install dist/semantic_pdf_search-0.8.0-py3-none-any.whl
```

## Launching semantic-pdf-search

Once installed, run the application from your command line:

```
semantic-pdf-search
```

### Basic Usage Guide

1.  **Browse for a PDF:** Click on "File ..." -> "Open ..." -> "Browse for PDF" to browse for a PDF file.
2.  **Select and Open:** Navigate to your PDF, select it, and click "Open".
3.  **Wait for Embeddings:** The application will process the document and create embeddings. This may take a moment, especially for large files.
4.  **Enter a Query:** Once the document is loaded, type your query into the search bar and press **Enter**.
5.  **View Results:** The application will display a list of page numbers that contain near-matches to your query.
6.  **Open the Page:** Click on any of the result buttons to open the PDF directly to that page in your default web browser.