# Exploring NLP and Information Extraction to Jointly Address Question Generation and Answering
===============

Sample source code for our [AIAI 2020](https://easyconferences.eu/aiai2020/) paper: [Exploring NLP and Information Extraction to Jointly Address Question Generation and Answering](https://link.springer.com/chapter/10.1007/978-3-030-49186-4_33)

> **Abstract:** Question Answering (QA) and Question Generation (QG) have been subjects of an intensive study in recent years and much progress has been made in both areas. However, works on combining these two topics mainly focus on how QG can be used to improve QA results. Through existing Natural Language Processing (NLP) techniques, we have implemented a tool that addresses these two topics separately. We further use them jointly in a pipeline. Thus, our goal is to understand how these modules can help each other. For QG, our methodology employs a detailed analysis of the relevant content of a sentence through Part-of-speech (POS) tagging and Named Entity Recognition (NER). Ensuring loose coupling with the QA task, in the latter we use Information Retrieval to rank sentences that might contain relevant information regarding a certain question, together with Open Information Retrieval to analyse the sentences. In its current version, the QG tool takes a sentence to formulate a simple question. By connecting QG with the QA component, we provide a means to effortlessly generate a test set for QA. While our current QA approach shows promising results, when enhancing the QG component we will, in the future, provide questions for which a more elaborated QA will be needed. The generated QA datasets contribute to QA evaluation, while QA proves to be an important technique for assessing the ambiguity of the questions.

**Authors:** Pedro Azevedo, Bernardo Leite, Henrique Lopes Cardoso, Daniel Castro Silva and Luís Paulo Reis 

If you use this research in your work, please kindly cite us:
```bibtex
@inproceedings{azevedo_2020_qgae,
	title        = {Exploring NLP and Information Extraction to Jointly Address Question Generation and Answering},
	author       = {Azevedo, Pedro and Leite, Bernardo and Cardoso, Henrique Lopes and Silva, Daniel Castro and Reis, Lu{\'i}s Paulo},
	year         = 2020,
	booktitle    = {Artificial Intelligence Applications and Innovations},
	publisher    = {Springer International Publishing},
	address      = {Cham},
	pages        = {396--407},
	isbn         = {978-3-030-49186-4},
	editor       = {Maglogiannis, Ilias and Iliadis, Lazaros and Pimenidis, Elias}
}
```

> This repository contains experimental software and is published for the sole purpose of giving additional background details on the respective publication.

## Prerequisites
```bash
Python 3
Java
```
> Note: This code has been tested with Python 3.9.5 in Mac OSX (High Sierra)

## Installation and Configuration
1. Clone this project:
    ```python
    git clone https://github.com/bernardoleite/nlp-ir-qg-qa
    ```
2. Install the Python packages from [requirements.txt](https://github.com/bernardoleite/nlp-ir-qg-qa/blob/main/requirements.txt). If you are using a virtual environment for Python package management, you can install all python packages needed by using the following bash command:
    ```bash
    cd nlp-ir-qg-qa/
    pip install -r requirements.txt
    ```
3. Download [StanfordCoreNLP (version 3.9.2)](http://nlp.stanford.edu/software/stanford-corenlp-full-2018-10-05.zip) and save it in the model's folder.

4. Download Spacys NLP Parsers:
    ```bash
    python -m spacy download en_core_web_sm
    python -m spacy download en_core_web_lg
    ```

5. (For mac/linux only) You may need to install libomp:
    ```bash
    brew install libomp 
    ```

## Usage
* You can run `src/questiongen.py` for generating questions from `src/texts/1.txt` sentences file (example).
* You can run `src/live_demo.py` for both generating and extracing answers from `src/texts/1.txt` sentences file (example).

## Issues and Usage Q&A
To ask questions, report issues or request features, please use the GitHub Issue Tracker.

## Contributing
Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement". Don't forget to give the project a star! Thanks in advance!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
This code is released under the **MIT** license. For details, please see the file [LICENSE](https://github.com/bernardoleite/nlp-ir-qg-qa/blob/main/LICENSE) in the root directory.

## Contact
* Bernardo Leite, bernardo.leite@fe.up.pt
* Pedro Azevedo