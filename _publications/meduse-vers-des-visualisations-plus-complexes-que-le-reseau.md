---
title: "Méduse, vers des visualisations plus complexes que le réseau"
year: 2017
venue: "Chronotopies : lecture et écriture des mondes en mouvement"
type: "chapter"
author: "Alexandre Rigal and Dario Rodighiero"
lang: fr
editor: "Guillaume Drevon and Luc Gwiazdzinski and Olivier Klein"
doi: "https://doi.org/10.5281/zenodo.3516222"
publisher: "Elya Éditions"
place: "Grenoble"
thumb: "meduse-vers-des-visualisations-plus-complexes-que-le-reseau/fig_001.webp"
---
Les visualisations en réseau comptent parmi les plus complexes qui soient ; pourtant, elles échouent parfois à rendre la complexité du réel : leurs relations ne suffisent pas à l’analyser, et elles ne distinguent pas les différences qualitatives entre les entités représentées. Partant du modèle classique du réseau, cet article propose une solution que nous nommons trajectoire — un réseau qui représente non seulement des distances, mais aussi des durées, et qui donne à voir des entités en mouvement selon leur évolution dans le temps. Construite sur une ligne de temps verticale, la trajectoire offre aux humanités numériques un nouveau langage visuel, et un outil pour porter leurs réseaux à la plus complexe des visualisations possibles.

<!--more-->

{% include figure-single.html class="three-quarter" src="/images/meduse-vers-des-visualisations-plus-complexes-que-le-reseau/fig_001.webp" caption="Le Caravage, _Méduse_, 1599, Galerie des Offices, Florence." %}

## Introduction

Les visualisations en réseau sont la plus complexe des visualisations possibles. Mais les visualisations en réseau constituent une forme qui n’épuise pas la description de la réalité. Même si ces visualisations sont parmi les plus utilisées aujourd’hui, elles possèdent tout de même des limites :

- premièrement, les relations représentées par les réseaux ne sont pas suffisantes pour analyser la complexité,
- deuxièmement, les réseaux ne distinguent pas les différences qualitatives entre les entités.

Partant d’un modèle réseau, comment modifier cette visualisation pour améliorer la compréhension de la richesse de la réalité ? Dans cet article, nous proposons une des réponses possibles, que nous nommons trajectoire. La trajectoire a deux points forts, en comparaison au réseau :

- premièrement, la trajectoire représente non seulement des distances, mais aussi des durées,
- deuxièmement, la trajectoire illustre comment une entité se meut, à travers ses évolutions dans le temps.

Le discours suivant est articulé autour de la combinaison de ces quatre points. Considérant que les réseaux sont des outils largement diffusés dans les humanités numériques, nous proposons un langage visuel alternatif pour améliorer les possibilités des représentations de données. Par cette tentative d’amélioration de la visualisation en réseau, nous offrons aux humanités numériques la plus complexe possible des visualisations. Et finalement, à la fin de l’article, nous découvrons que les arbres-réseau sont en fait des serpents qui dansent.

## Le réseau n’est pas encore assez complexe

Comment améliorer la complexité d’une visualisation ? Quel est le rôle du mouvement dans la représentation ? Pour répondre à ces questions, nous allons investiguer les qualités et les inconvénients d’une visualisation en réseau.

Le réseau est un outil très intéressant pour visualiser la réalité. Avec le modèle du réseau, des quantités illimitées de relations et d’entités peuvent être cartographiées. Le réseau ne trace pas des frontières : il n’impose pas de limites quantitatives à la réalité représentée. Comment prétendre alors, seulement imaginer une visualisation plus complexe ? Avec d’autres mots : comment dessiner une infinité encore plus grande de relations et d’entités ? De fait, c’est impossible : le réseau représente le nombre maximal de relations et d’entités possibles. Mais d’autres possibles s’offrent à nous : enrichir les entités des réseaux, en représentant la dimension temporelle de la réalité.

Les visualisations en réseau sont créées pour rendre compte de jeux de distance et d’attraction, autrement dit, pour représenter des relations spatiales. S’appesantissant sur une visualisation en réseau, Nietzsche se serait probablement écrié : « Spatial, trop spatial ». En effet, les visualisations en réseau sont des images stables, qui conservent immobile chaque entité, sans évolution possible. Il s’agit seulement d’une prise de vue de la réalité selon un moment unique. Au sein d’un réseau visualisé, la simultanéité prime : les entités sont comme dans un temps gelé. Ainsi, en souhaitant parvenir à une représentation encore plus détaillée de la complexité, il est nécessaire que nous introduisions une autre dimension aux relations des entités : la dimension du temps.

{% include figure-single.html class="three-quarter" src="/images/meduse-vers-des-visualisations-plus-complexes-que-le-reseau/fig_002.webp" caption="Figure 1. Le réseau du DHLAB est créé selon des données de co-écriture : chaque nœud représente un auteur et chaque ligne vaut pour une collaboration dans l’écriture d’un travail de recherche. Le réseau du DHLAB est assez étendu : cela signifie qu’il regroupe non seulement des membres du DHLAB, mais que des collaborateurs externes peuvent aussi constituer des nœuds s’ils ont participé à la rédaction d’un travail en commun avec un membre du DHLAB." %}

Le temps et l’espace sont nécessairement liés au mouvement. Pour accroître la richesse du langage visuel, spécialement s’il s’agit de réseaux, nous introduisons une manière de visualiser des entités en mouvement. Il n’est pas indispensable de représenter encore plus d’entités ou de relations, plutôt d’élaborer plus richement leur mode de représentation. Les entités trouvent leur prolongement selon l’axe du temps. De la sorte, la réalité va être représentée non plus en termes d’infinité spatiale, composée d’entités et de relations, mais selon l’infinité temporelle d’entités et de relations.

## Représenter le mouvement

Le mouvement est le concept qui couple la relation du temps et de l’espace, c’est pourquoi le mouvement est à dessiner, si l’on veut reproduire la complexité. Et le mouvement ne se représente pas seulement par des distances spatiales, mais aussi grâce à des durées. Si la visualisation en réseau doit représenter le mouvement, le réseau doit alors être fluidifié par une nouvelle dimension. C’est la raison pour laquelle notre but est de visualiser l’évolution d’entités grâce à une mise en séquence de réseaux, une séquence fondée sur le temps.

Kandinsky avait souligné à quel point les nœuds étaient désespérément figés (1947, 32–35). Visuellement parlant, les entités des réseaux sont représentées par des points. Pour créer des visualisations dynamiques, les nœuds doivent être mis en mouvement. De plus, Kandinsky poursuit : « Considered in terms of substance [the point], it equals zero » (1947, 25). Leur donner une image de mouvement signifie que les points ont à être représentés par des lignes (Kandinsky 1947, 57 ; Ingold 2007). Cette modification de la représentation nous permet de complexifier la pauvreté visuelle du point-nœud. Le contraste entre le point et la ligne dans les visualisations en réseau trouve une autre analogie avec les pensées de Kandinsky, qui pose la ligne comme l’antithèse complète du point : « The line is, therefore, the greatest antithesis to the pictorial proto-element – the point » (Kandinsky 1947, 57).

Grâce à l’usage de la ligne, la continuité va entrer dans la représentation, en tant que colle capable de lier de manière narrative une séquence de plusieurs réseaux. Habituellement, la juxtaposition de réseaux constitue un ensemble d’images statiques sans évolution. Si la visualisation en réseau est infinie du point de vue de l’espace, elle est vraiment pauvre pour rendre visible des relations temporelles, autrement dit une autre dimension d’une infinie complexité. L’introduction de la trajectoire offre au champ des visualisations en réseau une alternative plus riche : d’une infinité de durées liant relations et entités. Par l’introduction de lignes à la place des nœuds, la représentation des entités est complexifiée. La durée introduite par ces lignes n’est pas abstraite, il s’agit de la représentation du temps de l’évolution des entités elles-mêmes. Dans leur métamorphose, des points aux lignes, les entités en réseau prennent une forme visuelle qui occupe l’espace et le temps. Par cette proposition d’une alternative dans le dessin des entités, nous libérant des nœuds, nous enrichissons la complexité représentée des entités. Avec les trajectoires, elles ne sont plus autant standardisées (Munster 2013, 3) et fixées, mais leur évolution est rendue visible. Finalement, elles sont collectées au sein d’une représentation commune : « In short, all things equally exist, yet they do not exist equally » (Bogost 2012, 11).

## Un nouvel alphabet graphique pour visualiser des données spatiales et temporelles

Parvenus à ce point, renforcés par l’établissement des avantages et des faiblesses des visualisations en réseau, nous proposons l’alphabet des trajectoires : une composition élémentaire à la fois horizontale et verticale.

Comme toute visualisation, les réseaux sont produits à partir de données spécifiques. Les données de base nécessaires sont :

- le nombre de relations entre les entités,
- la mesure de la distance entre les entités.

Si, partant de là, nous tentons de construire une autre visualisation, nous avons besoin d’obtenir de nouvelles données : « each new visual environment demands […] new way of measuring » (Kepes 1995, 13). Souhaitant représenter les mouvements des entités dans le temps, nous avons besoin de données temporelles. Et les données qui concernent le temps sont de deux types : des processus et des événements. Pour être plus explicites, les trajectoires reposent sur plus de types de données différentes que le réseau :

- le nombre des relations entre les entités,
- la mesure de la distance entre les entités,
- la mesure de la durée de chaque entité,
- l’événement de l’apparition de chaque entité,
- l’événement de la disparition de chaque entité.

Travaillons strate par strate, et essayons de produire une sorte d’alphabet pour visualisation de trajectoires. Si nous souhaitons ajouter la durée aux nœuds, nous utilisons des lignes. Une ligne équivaut à une entité. Comme le réseau s’appuie sur des lignes horizontales, nous n’avons pas d’autre option que d’introduire le temps par des lignes verticales. Chaque naissance et chaque disparition d’entité est dessinée suivant la pointe d’une ligne verticale. La longueur, en tant que concept du temps (Kandinsky 1947, 98), permet au designer de données d’indiquer la durée des vies des entités.

Pour plus de clarté, mettons de côté la visualisation en réseau pour le moment. Dans cette première représentation de trajectoire, nous allons utiliser seulement les données temporelles de la liste ci-dessus — durée, apparition, disparition.

{% include figure-single.html class="half" src="/images/meduse-vers-des-visualisations-plus-complexes-que-le-reseau/fig_003.webp" caption="Figure 2. Modèle de trajectoire : les lignes verticales sont des entités hypothétiques ; leur longueur indique le nombre d’années ; le début et la fin de chaque ligne verticale donnent à lire l’apparition et la disparition de l’entité." %}

Avec l’usage des lignes, nous introduisons : la naissance, la fin, la longueur de la vie de chaque entité. Cependant, il y a encore des informations parallèles, notamment à propos de la simultanéité de l’évolution de chaque entité. Nous pouvons aussi nous intéresser aux successions, aux remplacements et à la stabilité des entités. Le temps est rendu dans sa complexité, dégivré par l’usage de lignes verticales. Les enquêtes à propos de l’évolution des entités deviennent plus aisées et ouvertes.

Après l’énumération des similarités et des différences entre la trajectoire et le réseau, nous pouvons résumer les propriétés de la trajectoire au sein d’une définition. La trajectoire représente le plus grand nombre possible d’entités par leurs relations temporelles. La trajectoire visualise la direction, l’évolution, l’apparition et la disparition des entités. Elle vise à rendre visuellement l’incertitude du temps.

Utiliser le réseau entraîne un effet de certitude, du fait de l’usage de lignes droites et d’un maillage sans fuite possible. De plus, le réseau n’est pas capable de proposer des récits (Venturini 2012, 50), alors que la narrativité est au fondement du travail d’interprétation des humanités. Pourtant, même de la sorte, il était impossible de prétendre que le réseau n’était pas un miroir parfait de la complexité de la réalité. Et c’est d’autant plus vrai avec la trajectoire. En augmentant le type et le nombre de données que nous mobilisons pour visualiser une trajectoire, dans le même temps, nous accroissons la difficulté d’obtenir des données, et l’incertitude de la visualisation. Une visualisation est une interprétation et ne peut pas assurer la transparence et l’équivalence (Drucker 2011). Les techniques de visualisation, automatiques ou non, sont une autre façon d’interpréter — et non de refléter — la réalité. Ce que les outils informatiques et automatiques incorporent est une autre forme d’action humaine (Simondon 2012), et les outils informatiques performent selon leur manière propre la réalité (Callon 1986 ; Haraway 1991).

Mais l’incertitude est aussi un problème double : l’incertitude est un résultat d’un travail qui comporte ses propres limitations, ce que nous souhaitons visualiser. Comment représenter l’incertitude tout en conservant la précision des données que nous possédons ? Nous essayons de révéler l’incertitude par l’usage de lignes courbées. Les lignes courbes, contrairement aux lignes droites, ne fabriquent pas une esthétique positiviste et unilatérale. L’incertitude est aussi présente dans les directions futures des lignes d’évolution et le dessin de leurs courbes : infinies, sans point final, seulement terminées par une ligne coupée en attente d’être poursuivie ou non. Chaque entité peut posséder des propriétés et des relations non découvertes. L’incertitude est à la fois l’état de la réalité (Meillassoux 2007), la limite de chaque visualisation de données, et le plus préférable des résultats d’un travail d’ouverture des possibles pour de futures recherches.

Partant de l’alphabet des trajectoires, nous proposons un cas d’étude pour explorer les usages possibles des trajectoires, au sein d’enquêtes.

{% include figure-single.html class="three-quarter" src="/images/meduse-vers-des-visualisations-plus-complexes-que-le-reseau/fig_004.webp" caption="Figure 3. Le réseau du DHLAB est divisé selon les années. Chaque trajectoire représente un auteur qui publie durant plusieurs années, traçant sa continuité au sein du contexte du laboratoire." %}

## Conclusion : de la tête figée de la Méduse-réseau aux serpents qui dansent sur la tête de Méduse-trajectoire

Dans le mythe, Persée tue Méduse en lui coupant la tête. Lorsqu’elle était vivante, la tête de Méduse était couverte de serpents dansants. Mais les serpents finissent inanimés, dans les mains du héros grec. Comme la tête de Méduse après l’assassinat de Persée, le réseau est coupé, séparé de la vitalité des entités et relations représentées. Les lignes du réseau sont figées. Pourquoi ne pas ressusciter les serpents qui dansent sur la tête de Méduse et tenter la proposition d’une image du mouvement de toutes les entités et relations entre elles ?

L’objectif en introduisant la méthode de trajectoire est de suivre les lignes de vie des entités et relations représentées. Le réseau, toujours utile, était la plus complexe des représentations possibles. Avec la trajectoire, les entités ne sont plus gelées. Pour conclure, nous avons démontré que les arbres (Lima 2014) sont en fait des serpents bien vivants. Réglant le problème de la représentation du mouvement grâce à des lignes, désormais, la trajectoire est la nouvelle visualisation la plus complexe possible.

## Bibliographie

- Bogost, Ian. 2012. _Alien Phenomenology, or What It’s Like to Be a Thing_. Minneapolis: University of Minnesota Press.
- Callon, Michel. 1986. “Éléments pour une sociologie de la traduction : la domestication des coquilles Saint-Jacques et des marins-pêcheurs dans la baie de Saint-Brieuc.” _L’Année sociologique_ 36.
- Drucker, Johanna. 2011. “Humanities Approaches to Graphical Display.” _Digital Humanities Quarterly_ 5 (1).
- Haraway, Donna. 1991. _Simians, Cyborgs and Women: The Reinvention of Nature_. New York: Routledge.
- Ingold, Tim. 2007. _Lines: A Brief History_. Londres: Routledge.
- Kandinsky, Wassily. 1947. _Point and Line to Plane_. New York: The Solomon R. Guggenheim Foundation for the Museum of Non-Objective Painting.
- Kepes, György. 1995. _Language of Vision_. New York: Dover.
- Lima, Manuel. 2014. _The Book of Trees: Visualizing Branches of Knowledge_. New York: Princeton Architectural Press.
- Meillassoux, Quentin. 2007. _Après la finitude : essai sur la nécessité de la contingence_. Paris: Seuil.
- Munster, Anna. 2013. _An Aesthesia of Networks: Conjunctive Experience in Art and Technology_. Cambridge: MIT Press.
- Simondon, Gilbert. 2012. _Du mode d’existence des objets techniques_. Paris: Aubier.
- Venturini, Tommaso. 2012. “Great Expectations : méthodes quali-quantitatives et analyse des réseaux sociaux.” In _L’Ère post-media : humanités digitales et cultures numériques_, dirigé par Jean-Paul Fourmentraux, 39–51. Paris: Hermann.
