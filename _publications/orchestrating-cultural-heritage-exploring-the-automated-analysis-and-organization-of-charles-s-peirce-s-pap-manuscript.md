---
title: "Orchestrating Cultural Heritage: Exploring the Automated Analysis and Organization of Charles S. Peirce’s PAP Manuscript"
year: 2023
venue: "ACM Conference on Hypertext and Social Media"
type: "conference"
author: "Davide Picca and Antonin Schnyder and Eri Kostina and Alessandro Adamou and Dario Rodighiero and Jeffrey Schnapp"
doi: "https://pure.rug.nl/ws/portalfiles/portal/780076742/3603163.3609066.pdf"
thumb: "@cards/Orchestrating-Cultural-Heritage.webp"
---
This preliminary study introduces an innovative approach to the analysis and organization of cultural heritage materials, focusing on the archive of Charles S. Peirce. Given the diverse range of artifacts, objects, and documents comprising cultural heritage, it is essential to efficiently organize and provide access to these materials for the wider public. However, Peirce’s manuscripts pose a particular challenge due to their extensive quantity, which makes comprehensive organization through manual classification practically impossible. In response to this challenge, our paper proposes a methodology for the automated analysis and organization of Peirce’s manuscripts. We have specifically tested this approach on the renowned 115-page manuscript known as PAP. This study represents a significant step forward in establishing a research direction for the development of a larger project. By incorporating novel computational methods, this larger project has the potential to greatly enhance the field of cultural heritage organization.

<!--more-->

## Introduction

Charles S. Peirce, a seminal figure in mathematics, logic, and philosophy, has profoundly impacted the intellectual evolution of humanity, particularly in the domain of scientific methodology (Burch 2001). However, the extensive intellectual heritage he left behind presents formidable challenges for organizing and categorizing it, due to constraints in accessibility and the task of organizing undated and revised texts.

Following Peirce’s passing, Harvard University assumed stewardship of roughly 100,000 manuscript pages inherited from his widow (Harvard Library 2022). Efforts to restructure and digitize Peirce’s archive have proven challenging due to the sheer volume of his work and the ambiguity surrounding its chronological order.

This presentation introduces preliminary findings from an upcoming government-funded initiative, led in conjunction by the University of Lausanne, Harvard Houghton Library, Groningen University, and Bibliotheca Hertziana, to digitize and computationally reorganize Peirce’s archive (Keeler 2020). The study outlined here proposes a method for examining and classifying Peirce’s manuscripts utilizing an automated system for more effective corpus organization.

The presentation is organized as follows: Section 2 elaborates on the complexities of the proposed classification, acknowledging Richard Robin’s catalog (Robin 1967) and the Peirce Edition Project (Peirce Edition Project 2021). Section 3 details the dataset and pre-processing measures, while Section 4 discusses the methodology for information extraction and initial findings, before concluding with an outlook on the next steps.

## Preserving Cultural Heritage

Cultural heritage encompasses a broad range of artifacts, objects, and documents that provide insights into the history, values, and cultural practices of society. Preserving cultural heritage is crucial for maintaining the memory of humanity’s collective past and understanding its evolution. In recent years, digitizing cultural artifacts has become a popular approach to making them more accessible to the broader public. However, organizing and categorizing digital collections of cultural heritage materials remains challenging.

Digitizing cultural heritage materials has several advantages, including the ability to make them more easily accessible to the public, to preserve fragile or deteriorating materials, and to facilitate research and study of the materials by scholars and researchers (Picca et al. 2022). However, simply digitizing materials is not enough — the materials must also be organized to make them searchable and navigable.

One example of the challenges faced when organizing cultural heritage materials can be seen in Charles S. Peirce’s manuscripts at Harvard Library. Peirce’s manuscripts were left in disarray at the library, and scholars have attempted to classify the documents in various ways (Harvard Library 2022). However, the quantity and nature of the manuscripts make it a daunting task. Houser (1989) notes that Peirce’s papers were eventually classified by scientific discipline, but the organization did not consider the development of Peirce’s thought. While the Hartshorne-Weiss volumes contributed significantly to categorizing Peirce’s papers, they were semi-problematic. The Peirce Edition Project aimed to collate Peirce’s writings chronologically, but a shortage of scholars and funding now threatens the project’s survival.

Richard Shale Robin’s catalog of Peirce’s manuscripts remains a vital resource for researchers, although Robin acknowledged its imperfections and suggested automating Peirce’s manuscript processing. Despite these challenges, preserving cultural heritage cannot be understated. Ongoing efforts to organize and digitize cultural heritage materials will help ensure these invaluable artifacts are available to future generations.

## Empirical Analysis

This presentation introduces the preliminary findings of an upcoming government-funded project, which aims to automate the organization of Peirce’s corpus, ensuring consistency and accuracy in content categorization. This analysis aims to showcase an automated methodology that can compare parts of one or multiple documents, thereby creating a scalable model that can be applied to extensive collections, including the unpublished manuscripts of Peirce himself.

The case study centralizes on Peirce’s renowned manuscript, PAP (Prolegomena for an Apology to Pragmatism), publicly available online through Houghton Library (Harvard Library 2022). Identified as “Ma 293” and classified under the pragmatism category in Robin’s catalog (Robin 1967), PAP represents one of Peirce’s most significant writings (Stjernfelt 2007). The current analysis examines all 115 manuscript pages of PAP, which include 56 pages of writing, 48 variant pages, and one blank page. These pages predominantly consist of textual content, with some inclusion of equations, graphs, and annotations. These statistics are summarized in Table 1.

The data obtained from this analysis was utilized for various purposes, as will be outlined in Section 4. High-level information about the entire text was acquired by merging all the pages into a single document. Depending on requirements, individual pages were examined separately or aggregated for comparison. For instance, the network illustrated in Section 4.2 was constructed from a knowledge graph extracted from all manuscript pages referred to as PAP, combined into a single file. Non-textual information was excluded from this analysis to focus entirely on text, as Peirce’s diagrams warrant a project in their own right. All the subsequent initial studies were conducted without considering potential contributions from these graphical elements.

<figure class="data-table narrow" markdown="1">

| Section | Page Number | Word Count | Word Percent |
|:--|--:|--:|--:|
| First Draft | 56 | 9,250 | 54.8% |
| Later Variants | 48 | 7,627 | 45.2% |
| Blank Pages | 1 | 0 | 0.00% |

<figcaption>Table 1. Comparison of word count between sections.</figcaption>

</figure>

## Methodology

The automated process discussed in this section follows a three-step procedure:

1. Initial processing of manuscript pages, including layout recognition and text transcription.
2. Semantic evaluation of pages and extraction of pertinent terms and connections.
3. Grouping of pages based on similar lemma use and presenting the groups through a cartographic visualization.

### Initial Processing

The first phase of our approach involves transcribing manuscript pages fetched from HOLLIS, the repository of Harvard University that holds Peirce’s archive (Harvard University 2023). TIFF images of the PAP document were locally downloaded using the International Image Interoperability Framework (IIIF), a protocol that delivers high-quality images and their corresponding metadata online for cultural heritage institutions (Snydman, Sanderson, and Cramer 2015). The 115-page images were then uploaded to the Transkribus platform (Kahle et al. 2017) for layout detection, Optical Character Recognition (OCR), and Handwritten Text Recognition (HTR). To minimize decoding errors, a manual revision followed this automated process. Given the focus on the handwritten text, figures, and graphs were replaced with a placeholder “Fig. x”, and unrecognized words were noted with <span style="white-space: nowrap">“||||unidentified-word||||”</span>. No similarities were detected among these unidentified words. The transcription was then exported to XML format for text analysis using the spaCy (Vasiliev 2020) and REBEL (Huguet Cabot and Navigli 2021) libraries.

### Text Analysis

Several computational techniques were employed to analyze the manuscript, taking into account Peirce’s unique writing style. The first technique involved identifying capitalized words, which Peirce used for emphasis, such as “Diagram”, “Induction”, or “Line of Identity”. The average ratio of capitalized words per page was 9.3, with a standard deviation of 8.7. Semantic proximity between manuscript pages was estimated using vector representations of words computed by spaCy. This approach created a square correlation matrix that displayed values between −1 and +1, indicating the proximity between each pair of documents (Figure 1). The latter variant pages were grouped and linked with the corresponding first draft pages, leading to 56 documents.

{% include figure.html class="three-quarter" src="/images/orchestrating-cultural-heritage-exploring-the-automated-analysis-and-organization-of-charles-s-peirce-s-pap-manuscript/fig_001.webp" alt="A triangular correlation matrix of 56 manuscript pages, with cells shaded from grey (low similarity) to red (high similarity) along the color scale." caption="Figure 1. Correlation matrix showing the semantic proximity of pages to each other. Variants have been aggregated." %}

The most frequent lemmas were also identified to better understand the manuscript’s meaning. After removing less significant words, lemmas were extracted and sorted in decreasing order of occurrence. This information was presented as a bar chart (Figure 2).

{% include figure.html class="three-quarter" src="/images/orchestrating-cultural-heritage-exploring-the-automated-analysis-and-organization-of-charles-s-peirce-s-pap-manuscript/fig_002.webp" alt="A horizontal bar chart of the most frequent lemmas in PAP, led by “pap”, “diagram”, “line”, “relation”, and “form”, decreasing in absolute count." caption="Figure 2. Bar chart showing the most frequent lemmas in the document." %}

Finally, a network analysis was performed using REBEL, a method presented by Huguet Cabot and Navigli (2021). A total of 950 triples were extracted, and 43 relations were identified. These include relations that carry a methodological or scholarly significance (e.g., “discoverer or inventor”, “practiced by”, “studied by”, or “used by”) as well as those with causal (e.g., “has cause”, “has effect”) or topological meanings (e.g., “part of”, “location”, and “country”): aligning them with standard ontologies is part of future work. These relations were presented separately in interactive graphs using Streamlit.

### Clustering

The final stage of the text analysis employs lemmas to chart manuscript pages onto a two-dimensional plane through cartographic data visualization. First, the contents of all the pages were reduced to a frequency table of lemmas, which was subsequently modified utilizing the TF-IDF metric to highlight the similarity between pages (Salton and Buckley 1988). Next, the multi-dimensional frequency of lemmas that describe each page is reduced to two dimensions on the Cartesian plane through UMAP dimensionality reduction (McInnes, Healy, and Melville 2018). The UMAP algorithm provides a spatial distribution of manuscript pages based on similarity, creating page clusters with similar usage of lemmas as illustrated in Figure 3.

{% include figure.html class="three-quarter" src="/images/orchestrating-cultural-heritage-exploring-the-automated-analysis-and-organization-of-charles-s-peirce-s-pap-manuscript/fig_003.webp" alt="A scatter plot of numbered manuscript pages positioned by similarity across a two-dimensional plane, forming loose clusters." caption="Figure 3. The UMAP algorithm maps PAP manuscripts according to similarity." %}

Advanced data visualization techniques can be employed to customize this embedding (Moon and Rodighiero 2020; Rodighiero 2021; Rodighiero and Romele 2022). Furthermore, word clouds display the most frequently used words in each cluster. This potential visual classification provides an alternative interpretation of the manuscript pages, in addition to close reading and typical text-analysis visuals. This two-dimensional classification of PAP writings can be extended to more extensive manuscript collections like the Peirce archive.

{% include figure.html src="/images/orchestrating-cultural-heritage-exploring-the-automated-analysis-and-organization-of-charles-s-peirce-s-pap-manuscript/fig_004.webp" alt="A web-based visualization of the UMAP embedding with contour lines enclosing four clusters, each labeled by a word cloud of its most frequent terms such as “reasoning”, “thought”, “definition”, and “relation”." caption="Figure 4. This web-based application allows the user to see the UMAP embedding with new graphical elements that resemble a visual classification of the PAP manuscript pages." %}

## Conclusion

The preliminary findings from this ongoing project have demonstrated the potential of an automated approach to categorize and analyze Peirce’s unpublished manuscripts. By implementing computational text transcription and analysis techniques, we have successfully identified semantic connections between different sections of the PAP document. The resulting cartographic visualization provides an intuitive representation of the manuscript’s structure and the relationships between its various parts.

The following steps of this project will involve refining the methodology and extending the analysis to other manuscripts in Peirce’s corpus. In addition, future research could incorporate the examination of graphical content, such as diagrams and equations, to provide a more comprehensive understanding of Peirce’s work.

## References

- Burch, Robert. 2001. “Charles Sanders Peirce.” In _The Stanford Encyclopedia of Philosophy_ (Summer 2022 ed.), edited by Edward N. Zalta. Stanford: Metaphysics Research Lab, Stanford University. https://plato.stanford.edu/archives/sum2022/entries/peirce/
- Harvard Library. 2022. “Charles S. Peirce Papers.” Harvard Library. https://library.harvard.edu/collections/charles-s-peirce-papers
- Harvard University. 2023. “Charles S. Peirce Papers.” HOLLIS for Archival Discovery. Accessed March 8, 2023. https://hollisarchives.lib.harvard.edu/repositories/24/resources/6437
- Houser, Nathan. 1989. “The Fortunes and Misfortunes of the Peirce Papers.” Arisbe: The Peirce Gateway. https://arisbe.sitehost.iu.edu/menu/library/aboutcsp/houser/fortunes.htm
- Huguet Cabot, Pere-Lluís, and Roberto Navigli. 2021. “REBEL: Relation Extraction by End-to-End Language Generation.” In _Findings of the Association for Computational Linguistics: EMNLP 2021_, 2370–81. Punta Cana: Association for Computational Linguistics. https://aclanthology.org/2021.findings-emnlp.204
- Kahle, Philip, Sebastian Colutto, Günter Hackl, and Günter Mühlberger. 2017. “Transkribus — A Service Platform for Transcription, Recognition and Retrieval of Historical Documents.” In _2017 14th IAPR International Conference on Document Analysis and Recognition (ICDAR)_, 4:19–24. Kyoto: IEEE. https://doi.org/10.1109/ICDAR.2017.307
- Keeler, Mary. 2020. “Pragmatically Improving Access to Peirce’s Archive.” _Chinese Semiotic Studies_ 16 (1): 167–87. https://doi.org/10.1515/css-2020-0009
- McInnes, Leland, John Healy, and James Melville. 2018. “UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction.” arXiv. https://arxiv.org/abs/1802.03426
- Moon, Chloe Ye Eun, and Dario Rodighiero. 2020. “Mapping as a Contemporary Instrument for Orientation in Conferences.” In _The Inevitable Turning Point: Challenges and Perspectives for Humanistic Informatics. Proceedings of the IX Annual Conference of the Association for Humanities and Digital Culture (AIUCD)_, edited by Carlo Passarotti, Eleonora Maria Gabriella Litta Modignani Picozzi, Greta Franzini, and Cristina Marras, 156–62. Milan: Associazione per l’Informatica Umanistica e la Cultura Digitale. https://doi.org/10.5281/zenodo.3611340
- Peirce Edition Project. 2021. “Peirce Edition Project.” https://peirce.iupui.edu/
- Picca, Davide, Alessandro Adamou, Yumeng Hou, Mattia Egloff, and Sarah Kenderdine. 2022. “Knowledge Organization of the Hong Kong Martial Arts Living Archive to Capture and Preserve Intangible Cultural Heritage.” In _Digital Humanities 2022: Conference Abstracts_, 329–32. Tokyo: University of Tokyo. https://dh2022.dhii.asia/abstracts/files/PICCA_Davide_Knowledge_organization_of_the_Hong_Kong_Martial.html
- Robin, Richard S. 1967. _Annotated Catalogue of the Papers of Charles S. Peirce_. https://peirce.sitehost.iu.edu/robin/rcatalog.htm
- Rodighiero, Dario. 2021. _Mapping Affinities: Democratizing Data Visualization_. Open-access English ed. Geneva: Métis Presses. https://doi.org/10.37866/0563-99-9
- Rodighiero, Dario, and Alberto Romele. 2022. “Reading Network Diagrams by Using Contour Lines and Word Clouds.” In _Proceedings of Graphs and Networks in the Humanities_. Amsterdam: Royal Netherlands Academy of Arts and Sciences. https://doi.org/10.31235/osf.io/3g7bt
- Salton, Gerard, and Christopher Buckley. 1988. “Term-Weighting Approaches in Automatic Text Retrieval.” _Information Processing & Management_ 24 (5): 513–23. https://doi.org/10.1016/0306-4573(88)90021-0
- Snydman, Stuart, Robert Sanderson, and Tom Cramer. 2015. “The International Image Interoperability Framework (IIIF): A Community & Technology Approach for Web-Based Images.” In _Proceedings of the IS&T Archiving Conference_, 16–21. Los Angeles.
- Stjernfelt, Frederik. 2007. _Diagrammatology: An Investigation on the Borderlines of Phenomenology, Ontology, and Semiotics_. Synthese Library 336. Dordrecht: Springer.
- Vasiliev, Yuli. 2020. _Natural Language Processing with Python and spaCy: A Practical Introduction_. San Francisco: No Starch Press.
