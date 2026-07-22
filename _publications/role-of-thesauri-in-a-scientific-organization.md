---
title: "Role of Thesauri in a Scientific Organization"
year: 2009
venue: "Networks of Design"
type: "conference"
author: "Carlo Ferigato and Giuseppe Merlo and Daniela Panfili and Dario Rodighiero"
editor: "Fiona Hackney and Jonathan Glynne and Viv Minton"
publisher: "Universal-Publishers"
place: "Boca Raton, FL"
pages: "301–9"
isbn: "978-1-59942-906-9"
doi: "https://publications.jrc.ec.europa.eu/repository/handle/JRC48348"
thumb: "role-of-thesauri-in-a-scientific-organization/fig_002.webp"
---
We aim at describing the mediation language between users and indexers in a document retrieval system for a big scientific community intimately related to European Union policies. We argue that this mediation can be represented at three levels by thesauri. At the first level, thesauri are sets of indexes coordinating searches by means of term-to-term relations such as Narrower Term and Related Term. At a higher level, person-to-term relations follow from the use of thesauri for indexing and retrieval, while person-to-person relations are embodied in a thesaurus through the implicit representation of the organization it serves. In this way, thesauri constitute a network of mediation with historical, social, scientific and technological perspectives, the latter two owing to the scientific community they serve — and, in particular, to the network originally proposed by the Euratom Thesaurus (1966, 1967) and to a more recent thesaurus designed for the Joint Research Centre of the European Commission.

<!--more-->

## Introduction

The association of indexes to sets of documents for ordering them, as well as the organization of indexes in maps as mnemonic tools, is part of the history of mankind (Mangani 2006; Serrai 1997). Indexes are terms of a formal language allowing one to indicate sets of documents, where “indicate” carries both the meaning of “giving name” and “attributing a quality.” If the set of index terms is controlled in some way, it is said to be a controlled vocabulary — a specific subject of investigation in Library Science, whose importance can be expressed by quoting the introduction of a fundamental text in the field:

> This book deals with properties of vocabularies for indexing and searching document collections; the construction, organization, display, and maintenance of these vocabularies; and a vocabulary as a factor affecting the performance of a retrieval system. (Lancaster 1972: vii)

A controlled vocabulary ordered by a set of relations between its index terms is called a thesaurus. Graphically, a thesaurus can be displayed as a net whose vertices are indexes and whose meshes are formed by drawing the binary relations between indexes as arcs.

In this work, we deal with specific thesauri designed for the Joint Research Centre of the European Commission (the JRC) and discuss their use from three perspectives, in the sections “Networks of People,” “Networks of Terms and People,” and “Networks of Terms” below. By network of terms we mean the thesaurus together with its history and the choices made while designing it. We claim that a thesaurus is more than a formal language used in Library Science as a tool for the “manipulation of classes” of documents: it captures some of the characters of the community it serves. As a network of terms, a thesaurus can be used in many ways — for keeping a collection of documents ordered, for measuring the consistency and quality of a collection, and as a formal mediation language for information retrieval purposes.

Upon a thesaurus two more networks can be built. In “Networks of Terms and People,” the relations between people and descriptors are analysed; these relations link people to subjects of interest much as in a recommender system. In “Networks of People,” we describe the organization for which the thesauri were designed, aiming to describe the mutual relations between the structure of a thesaurus and the structure of the organization. In “Networks of Terms,” a thesaurus for nuclear science developed by a group of indexers and researchers in the same community (Euratom Thesaurus 1966, 1967) is described in detail, and the project for a new thesaurus for the JRC is presented.

The practical outcome of our work is the design of a new information retrieval system for the JRC, based on the new thesaurus presented in “Networks of Terms.” This system, called SIRS (Scientific Information Retrieval System), is built by considering both the history of the JRC and the analysis of a thesaurus as a formal language, as in “Networks of Terms and People.” While performing this task, we used as conceptual tools some of the Communication Disciplines introduced by Carl Adam Petri (1977, 2001) for analysing computerized systems seen as a “general medium for strictly organized information flow.” Our work in designing SIRS is reported in “SIRS Thesauri.” Conclusions and ideas for continuing our work are reported in the last section.

## Networks of People

By network of people we consider the professional relations among the members of a given scientific organization through its history. In particular, the Joint Research Centre of the European Commission — with attention to its Italian establishment — is the object of our work. The JRC was formally established by Article 8 of the Euratom Treaty (1957). We remark that, with the same article establishing the JRC, the mandate for establishing a uniform terminology concerning the object of the JRC’s work was given:

> After consulting the Scientific and Technical Committee, the Commission shall establish a Joint Nuclear Research Centre. This Centre shall ensure that the research programmes and other tasks assigned to it by the Commission are carried out. It shall also ensure that a uniform nuclear terminology and a standard system of measurements are established. (Euratom Treaty 1957, art. 8)

After a period of stability in the research themes from 1962 to 1971, a progressive enlargement of the fields of research occurred, together with a strong dependence of the research themes on policy acts and multi-annual work programmes approved by the Council.

Concerning the scientific activities of the Italian establishment of the JRC, its present activities are illustrated by the organizational chart in Figure 1. A comparison with the scientific activities reported by Gueben (1962) shows a deep enlargement of interests:

> Physique des Réacteurs (Physique Mathématique Appliquée, Physique Neutronique, Essais Critiques, Automatisme et Régulation); Matériaux (Métallurgie; Chimie; Physico-Chimie); Engineering (Technologie; Echange Thermique); Bibliothèque et Documentation; Neutronique Expérimentale et Conversion Directe; Physique Sanitaire, Médecine et Santé. (Gueben 1962: 3–4)

{% include figure.html src="/images/role-of-thesauri-in-a-scientific-organization/fig_001.webp" class="full" caption="Figure 1. Organizational chart (2008) of the JRC, excerpt for the main scientific activities at the Ispra site. Source: Organizational Chart (2008)." %}

While the JRC research themes in 1962 and the Euratom Thesaurus could be superposed completely, this operation cannot be done for the present research fields. Consequently, while in the period 1962–71 the Euratom Thesaurus was a complete representation of the JRC’s scientific interests, this is no longer true today. A proposal for a combination of thesauri allowing for an explicit representation of both the organization and the research activities is presented in “SIRS Thesauri” below.

## Networks of Terms and People

We assume that coordination among people participating in an organization is performed via language. The role of language in organizations, and its use as a modelling tool, is a deep subject of study. A survey of approaches based on linguistics, philology and pragmatics is reported in Bazerman and Paradis (1991). From the perspective of computer science, models of conversations have been used as representatives of organizations since the design of the program Coordinator (Winograd and Flores 1986), and originated a rich debate in the world of Computer Supported Cooperative Work (CSCW), well summarized by Giorgio De Michelis (2007). In these approaches, organizations are represented through the conversations of their members; this type of representation does not touch the individual terms used in conversations, but some high-level representation of the conversations themselves. Applications using some sort of controlled vocabulary already exist — these are called recommender systems (see the content-based methods in Adomavicius and Tuzhilin 2005), where people are represented by index terms.

In this work, we assume the existence of a formal language, a controlled vocabulary endowed with binary relations. The resulting relational structure — the thesaurus — is our modelling tool. Our use of a thesaurus as a linguistic representation tool is a compromise between the explicit representation of conversations and the simple use of index terms for representing people.

A thesaurus can be seen as representative of an organization in the following three ways:

- As Blair (1990) argues, information retrieval is a process of communication:

  > If we understand that the description of documents for retrieval, and the formulation of search requests, are fundamentally linguistic acts, then it is no great conceptual leap to see that information retrieval is fundamentally a process of communication. Inquirers are trying to describe the information they need in a way that indexers would understand, and indexers (or automatic indexing procedures) are trying to describe the content and context of documents in the collection in ways that would be understandable to the inquirers. (Blair 1990: 188)

  It is obviously not a process of communication as in the explicit representation of speech acts in the Coordinator application mentioned above, since here the operations of indexing and inquiring are not synchronous.

- Rolling (1966), while remaining at a practical level of description, sees the thesaurus as a kind of machine language apt for mechanical processing:

  > The intricacies of natural language, as it occurs in the texts of documents and abstracts, make it unsuitable for machine analysis. Computer retrieval requires a controlled vocabulary in which ideally each descriptor stands for one concept only. (Rolling 1966: 96)

  By extending this view to a wider game of language played between indexers and inquirers, we simplify the interactions among people to those it is possible to play on a thesaurus seen as a kind of terminological chessboard.

- At least in a simple way, a thesaurus also contains a structural representation of the organization it serves.

Consequently, the games of language played on it have multiple levels. The first level, a formal mediation language between library services and the people using them, contains more than a list of terms and their mutual abstract relations. If well designed, a thesaurus pragmatically allows for games of language intimately related to the structure and interests of the organization it serves. As a simple example, to look at the interests of a group inside a large organization, it is normal practice to look at how the documents produced by that group are indexed. In our view, language games are played at three levels: inter-organization, organization–policy, and organization–research. The organization–policy level results clearly from the JRC’s history after 1971, with the progressive enlargement of research themes and their implementation via research Actions.

In “SIRS Thesauri” below, we use these considerations as grounds for a new controlled language and thesaurus for the JRC.

## Networks of Terms

The Euratom Thesaurus (1966, 1967) was designed by the Center for Information and Documentation (CID) following the mandate of the Euratom Treaty. The CID was created in 1961 by the European Atomic Energy Community (Rolling 1966), and followed the merging of the European Coal and Steel Community, the European Atomic Energy Community and the European Economic Community into a single entity in 1967 (Brée 1972). The Euratom Thesaurus, whose first edition was published in 1964, was very advanced: its terminology charts are still quoted in the library science literature (Aitchison, Gilchrist, and Bawden 2000) as one of the first examples of graphical display.

{% include figure.html src="/images/role-of-thesauri-in-a-scientific-organization/fig_002.webp" class="full" caption="Figure 2. Terminological chart no. 53, “Reactor Operation.” Source: Euratom Thesaurus (1966, 1967)." %}

The Euratom Thesaurus served as a tool for subject control at the CID, in order to supply scientists of the European Atomic Energy Community and industry in its member countries with documentary information on all aspects of nuclear energy. Its terms were not limited to nuclear physics and reactor technology, but covered many related topics such as radiation protection, isotope technology, the fabrication and use of nuclear materials and instruments, radiochemistry, and radiobiology.

The graphic display of the Euratom Thesaurus is realized by terminology charts, as in Figure 2, in which terms are synthetically represented in clusters of descriptors, non-descriptors and forbidden terms; the strength of a relation between two terms is represented by the thickness of the arc. While the Euratom Thesaurus is a tool well designed from many perspectives, it no longer fits the retrieval needs of the JRC. A new thesaurus — indeed the combination of three thesauri — has consequently been developed for the Scientific Information Retrieval System of the JRC.

## SIRS Thesauri

The history of the JRC, the evolution of its research themes, and the progressive need for a close connection between European Union policy and research activities require a new controlled language for its information retrieval system. In designing it, we followed the interpretation given by Blair (1990) and assumed that a retrieval system models a process of communication. The controlled language used in this system is consequently a kind of terminological chessboard, on which language games — informing the process of communication — are played.

These language games have the general character of inquirer–indexer games played at three levels. The first level concerns the collection of documents, the traditional extent of a controlled language. The second level concerns the internal organization of the JRC, and acts as a kind of recommender system since it groups different activities around the same term. The third level is intimately related to the existence of the JRC and associates its research themes with the general policy indications of the European Union.

In the following sections we analyse these language games in more detail and propose three distinct thesauri for them, representing three distinct perspectives on the JRC — the internal organization, the policy, and the general research index. We then briefly describe how these three thesauri are integrated.

### Internal Organization

The Actions thesaurus is a simple scheme derived from the scientific part of the organizational chart of the JRC; all of its terms have a direct connection with the organizational chart. The finest representation of scientific activities is given by the so-called Actions, small groups of 5 to 20 researchers. Actions are not represented in the organizational chart, but have hierarchical dependence on its leaves. A few of the 120 JRC Actions active in 2008 are reported as an example in Table 1, where IPSC is the Institute for the Protection and Security of the Citizen and IES the Institute for Environment and Sustainability (see Figure 1).

<figure class="data-table" markdown="1">

| Action | Unit | Institute |
|:--|:--|:--|
| Maritime Surveillance | Maritime Affairs | IPSC |
| Community Image Data Portal | Agriculture | IPSC |
| Geo-Information Management and Control Methods | Agriculture | IPSC |
| Systematic Observations of Land and Ocean | Global Environment Monitoring | IES |
| Sustainable Transport | Transport and Air Quality | IES |

<figcaption>Table 1. JRC Actions active in 2008 and their hierarchical dependence on the organizational chart.</figcaption>
</figure>

### Policy

In 1981 the European Parliament and the Publications Office decided to establish a thesaurus for the organization of parliamentary acts. A first edition of the thesaurus — now called Eurovoc — was published in 1984 in seven Community languages. The Eurovoc Thesaurus (2007) presently contains 6,645 index terms; it is constantly updated and translated into 21 EU languages.

### General Research Index

The Dewey Decimal Classification (DDC) was conceived by Melvil Dewey in 1873 and published for the first time in 1876 (Dewey 1996). The DDC system is one of the most widely used library classification systems, strictly based on a hierarchical structure supported by decimal-number labelling.

### Integration of Thesauri

The overall thesaurus of the Scientific Information Retrieval System, SIRS, is the combination of the three thesauri above — Actions, Eurovoc and DDC. To create a unique relational system, the three thesauri must be joined; this is possible through a mapping procedure creating two sets of cross-thesauri relations: one connects Actions terms to Eurovoc terms, the other relates Eurovoc terms to DDC terms.

The mapping procedure is a task for the person responsible for SIRS contents, who has two main duties: the first is to describe what an Action is by using Eurovoc terms — traditional indexing applied to Actions instead of books; the second is to connect each DDC term already used for classifying the JRC Central Library holdings to one or more Eurovoc terms.

{% include figure.html src="/images/role-of-thesauri-in-a-scientific-organization/fig_003.webp" class="three-quarter" caption="Figure 3. The Action “Emissions Characterization and Inventories” indexed by Eurovoc terms." %}

As an example, the cross-thesauri mapping of the Action “Emissions Characterization and Inventories” with Eurovoc is shown in Figure 3. While the focus of SIRS is on this Action, it is possible to display other Actions as context; the context is computed on the number of common index terms in Eurovoc. In the example in Figure 3, the Action “Radioactivity Environmental Monitoring” shares six Eurovoc indexes with “Emissions Characterization and Inventories,” so the two Actions are consequently mutually close. An example of the final display, including the DDC cross-thesauri relations, is shown in Figure 4.

{% include figure.html src="/images/role-of-thesauri-in-a-scientific-organization/fig_004.webp" class="full" caption="Figure 4. The SIRS interface: the three thesauri on the left, retrieved items in the right-hand frames." %}

The SIRS interface is dynamic and designed in agreement with the Focus+Context paradigm (Spence 2007): when the user’s focus changes, the displayed frames do not disappear from the interface — they are resized and lose definition.

## Conclusion

We described our view on the role that a formal language for information retrieval and classification plays in modelling an organization, across three layers:

1. Layer of people. How the history of an organization gives birth to a network of terms, and changes it.
2. Layer of terms and people. From the plain proximity of people’s interests, reached through common indexes, to the more complex role of the network of terms as a mediation language between inquirers and indexers.
3. Layer of terms. Index terms, their mutual relations, and how a thesaurus can be seen as a formal linguistic tool.

We then used this analysis for the design of an information retrieval system, aiming to make explicit relations such as research themes to policy, or the mutual closeness of research themes. In doing so, we drew on conceptual tools from library science, pragmatics, information retrieval and computer science.

More work remains to be done, since we have only shallowly touched the problem of a thesaurus as a mediation language: its use as a mediation language between humans and non-humans, and among non-humans, is still to be undertaken. Moreover, a precise analysis of the translation (Latour 1996) of classification and retrieval disciplines to the computerized world remains to be done as well. We aim to continue our work in this direction, by analysing the historical development of the first formats for automatic library interchange of bibliographic data (MARC 1975) and the first tools for distributed indexing (Harvest 1999), reading their history in the light of thesauri seen as a main component of formal mediation languages.

## References

- Adomavicius, Gediminas, and Alexander Tuzhilin. 2005. “Toward the Next Generation of Recommender Systems: A Survey of the State-of-the-Art and Possible Extensions.” *IEEE Transactions on Knowledge and Data Engineering* 17 (6): 734–49.
- Aitchison, Jean, Alan Gilchrist, and David Bawden. 2000. *Thesaurus Construction and Use: A Practical Manual*. London: Aslib.
- Bazerman, Charles, and James Paradis, eds. 1991. *Textual Dynamics of the Professions*. Madison, WI: University of Wisconsin Press.
- Blair, David C. 1990. *Language and Representation in Information Retrieval*. Amsterdam: Elsevier.
- Brée, R. 1972. “European Community, Center for Information and Documentation.” In *Encyclopedia of Library and Information Science*, vol. 8, edited by Allen Kent et al. New York: M. Dekker.
- De Michelis, Giorgio. 2007. “The Contribution of the Language-Action Perspective to a New Foundation for Design.” In *HCI Remixed*, edited by Thomas Erickson and David W. McDonald, 293–99. Cambridge, MA: MIT Press.
- Dewey, Melvil. 1996. *Dewey Decimal Classification and Relative Index*. 21st ed. Albany, NY: Forest Press.
- Euratom Thesaurus. 1966. *Part I, Indexing Terms Used within Euratom’s Nuclear Documentation System*. EUR Report 500.e. Brussels: Information and Documentation Center.
- Euratom Thesaurus. 1967. *Part II, Terminology Charts Used in Euratom’s Nuclear Documentation System*. EUR Report 500.e. Brussels: Information and Documentation Center.
- Euratom Treaty. 1957. *Treaty Establishing the European Atomic Energy Community*, 298 U.N.T.S. 140, as amended in *Treaties Establishing the European Communities*. Brussels: EC Official Publications Office, 1987.
- Eurovoc Thesaurus. 2007. Vol. 1, *Permuted Alphabetical Version*, parts A and B; vol. 2, *Subject-Oriented Version*. Luxembourg: Office for Official Publications of the European Communities.
- Gueben, G. 1962. *Ispra, Centre Commun de Recherche de l’Euratom*. EUR Report 54.f. Originally published in *Bulletin d’Information de l’Association Belge pour le Développement Pacifique de l’Energie Atomique* 37.
- Harvest. 1999. “Harvest Web Indexing Package.” Accessed September 26, 2008. http://sourceforge.net/projects/webharvest/.
- Lancaster, F. Wilfrid. 1972. *Vocabulary Control for Information Retrieval*. Washington, DC: Information Resources Press.
- Latour, Bruno. (1992) 1996. *Aramis, or the Love of Technology*. Cambridge, MA: Harvard University Press.
- Mangani, Giorgio. 2006. *Cartografia Morale*. Modena: Franco Cosimo Panini.
- MARC. 1975. “Machine-Readable Cataloguing Program.” In *Encyclopedia of Library and Information Science*, vol. 16, edited by Allen Kent et al. New York: M. Dekker.
- Organizational Chart. 2008. “Organizational Chart of the JRC in July 2008.” Accessed August 27, 2008. http://www.europa.eu/.
- Petri, Carl Adam. 1977. “Communication Disciplines.” In *Proceedings of the Joint IBM University of Newcastle upon Tyne Seminar*, edited by B. Shaw, 171–83. Newcastle upon Tyne: University of Newcastle upon Tyne.
- Petri, Carl Adam. 2001. “Cultural Aspects of Net Theory.” *Soft Computing* 5: 141–45.
- Rolling, L. N. 1966. “A Computer-Aided Information Service for Nuclear Science and Technology.” *Journal of Documentation* 22 (2): 93–115.
- Serrai, Alfredo. 1997. *Storia della Bibliografia*. Vol. 8, *Sistemi e Tassonomie*. Rome: Bulzoni Editore.
- Spence, Robert. 2007. *Information Visualization: Design for Interaction*. 2nd ed. New York: Addison Wesley.
- Winograd, Terry, and Fernando Flores. 1986. *Understanding Computers and Cognition: A New Foundation for Design*. Norwood, NJ: Ablex.
