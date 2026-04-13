# Elections go bananas: A First Large-scale Multilingual Study of Pluralia Tantum using LLMs

This repository includes the evaluation scripts used in the paper.

## Citation

```bibtex
@inproceedings{spaziani-etal-2026-elections,
    title = "Elections go bananas: A First Large-scale Multilingual Study of Pluralia Tantum using {LLM}s",
    author = "Spaziani, Elena  and
      Zeinalipour, Kamyar  and
      Cassotti, Pierluigi  and
      Tahmasebi, Nina",
    editor = "Demberg, Vera  and
      Inui, Kentaro  and
      Marquez, Llu{\'i}s",
    booktitle = "Proceedings of the 19th Conference of the {E}uropean Chapter of the {A}ssociation for {C}omputational {L}inguistics (Volume 1: Long Papers)",
    month = mar,
    year = "2026",
    address = "Rabat, Morocco",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2026.eacl-long.308/",
    doi = "10.18653/v1/2026.eacl-long.308",
    pages = "6547--6570",
    ISBN = "979-8-89176-380-7",
    abstract = "In this paper, we study the expansion of pluralia tantum, i.e., defective nouns which lack a singular form, like scissors. We base our work on an annotation framework specifically developed for the study of lexicalization of pluralia tantum, namely Lexicalization profiles. On a corresponding hand-annotated testset, we show that the OpenAI and DeepSeek models provide useful annotators for semantic, syntactic and sense categories, with accuracy ranging from 51{\%} to 89{\%}, averaged across all feature groups and languages. Next, we turn to a large-scale investigation of pluralia tantum. Using dictionaries, we extract candidate words for Italian, Russian and English and keep those for which the changing ratio of singular and plural form is evident in a corresponding reference corpus. We use an LLM to annotate each instance from the reference corpora according to the annotation framework. We show that the large amount of automatically annotated sentences for each feature can be used to perform in-depth linguistic analysis. Focusing on the correlation between an annotated feature and the grammatical form (singular vs. plural), patterns of morpho-semantic change are noted."
}
```
