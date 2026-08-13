---
title: "Il Thesaurus del Nuovo soggettario interpreta SKOS"
year: 2010
venue: "AIDAinformazioni"
type: "journal"
lang: it
author: "Marta Motta and Dario Rodighiero"
doi: "https://doi.org/10.1400/212474"
volume: "4"
issue: "3"
pages: "75–87"
issn: "1121-0095"
thumb: il-thesaurus-del-nuovo-soggettario-interpreta-skos/cover.webp
---
Il consorzio W3C propone SKOS come standard per tutti i vocabolari controllati, in modo da creare un linguaggio che permetta di realizzare una rete informativa interoperabile. La Biblioteca nazionale centrale di Firenze ha deciso di sperimentare questo nuovo linguaggio formale. Qui di seguito viene trattato il caso studio della conversione in SKOS del Thesaurus del Nuovo soggettario, illustrandone vantaggi e problematiche.

<!--more-->

## Introduzione

Negli ultimi anni è ormai assodata l’utilità degli strumenti elaborati nell’ambito delle scienze documentali e bibliotecarie per l’organizzazione della conoscenza e l’architettura dell’informazione. L’avvento di Internet ha cambiato i modi con i quali l’informazione prende forma e viene organizzata, e questo ha avuto delle conseguenze anche nel campo dell’indicizzazione semantica e del recupero dell’informazione, in cui diventa sempre più importante elaborare strumenti che favoriscano la comunicazione e l’efficacia informativa non solo dei cataloghi delle biblioteche, ma di sistemi di organizzazione della conoscenza più in generale.

Nell’attuale contesto, caratterizzato da un gran numero di risorse informative virtualmente disponibili, gli strumenti per l’organizzazione dell’informazione e della conoscenza devono essere in grado di raggiungere i massimi livelli di efficacia e di efficienza, ossia devono produrre il risultato desiderato dall’utente nella maniera meno dispendiosa in termini di procedure, tempo e costi.

Il trasferimento di informazioni sul contenuto concettuale dei documenti mediante strutture formalizzate è un’attività che riguarda molti campi del sapere, come viene confermato anche a livello internazionale, grazie alle esperienze che mirano ad allestire sistemi che possano integrarsi fra loro pur nella diversità delle singole applicazioni. È quindi sempre più urgente l’interconnessione di linguaggi documentari tradizionali con tecniche di indicizzazione e recupero per soggetto (anche di risorse digitali) nell’ambito delle nuove prospettive di interoperabilità offerte dal web. Come sostiene Elaine Svenonius nel suo libro *The Intellectual Foundation of Information Organization* (2000), un’intelligente e corretta organizzazione dell’informazione è indispensabile non solo per la comunità scientifica, ma anche per i singoli, per l’economia e per la società in generale. Inoltre i principi, gli obiettivi e le tecniche fino ad oggi sviluppate per organizzare l’informazione nel campo degli studi biblioteconomici costituiscono senza dubbio un corpo di conoscenza ampiamente applicabile anche al nuovo contesto dell’era digitale.

Gli attori in gioco sono vari, si va dai thesauri alle tassonomie, dagli schemi di classificazione alle ontologie, ormai definiti come sistemi di organizzazione della conoscenza (KOS). Essi sono gli strumenti a disposizione per ottenere comprensione e comunicazione tra operatori e utenti di diverse aree linguistiche, ma anche per connettere risorse informative di differenti aree tematiche o domini disciplinari.

Gli strumenti di controllo terminologico non solo orientano gli utenti nel recupero delle informazioni (information retrieval), ma soprattutto normalizzano la terminologia attraverso metodi di analisi concettuale coerenti con l’assetto delle specifiche aree disciplinari, creando strutture basilari per l’organizzazione e la gestione delle informazioni.

In questo contesto i thesauri si sono dimostrati come eccellenti strumenti per assegnare metadati semantici (Broughton 2008), dal momento che la loro struttura consente una gestione efficace di questi metadati. Le relazioni dei thesauri, soprattutto quando questi sono integrati con cataloghi online di biblioteche, portali e siti web, sono utilissime per navigare nelle collezioni di risorse documentali e consentono di esplorare i materiali collegati allargando o restringendo la ricerca, attraverso termini più generici (BT) e termini più specifici (NT), oppure anche proponendo itinerari di avvicinamento attraverso i termini correlati (RT). La stessa presentazione sistematica e a volte classificatoria dei thesauri sembra fatta apposta per favorire la navigazione, particolarmente per le risorse digitali attraverso collegamenti ipertestuali.

Il nostro contributo vuole presentare i risultati di una sperimentazione: la conversione in SKOS (Simple Knowledge Organization System) del Thesaurus del Nuovo soggettario, di cui ci siamo occupati grazie alla collaborazione di Maria Grazia Pepe del settore Servizi informatici della Biblioteca nazionale centrale di Firenze. SKOS è lo standard del W3C per rendere disponibili sul web i sistemi di organizzazione della conoscenza. Il Thesaurus del Nuovo soggettario costituisce la componente terminologica del nuovo sistema di indicizzazione per soggetto impiegabile da biblioteche, archivi, mediateche, ecc.

La nostra riflessione sulle problematiche e le criticità riscontrate durante il processo di conversione si è basata anche, comparativamente, sulle soluzioni adottate da altri sistemi di indicizzazione come LCSH,[^1] RAMEAU[^2] e thesauri specialistici come LIUC[^3] e MESH,[^4] che negli ultimi anni hanno intrapreso la strada della traduzione in SKOS.

## Il Thesaurus del Nuovo soggettario

Il Nuovo soggettario è un progetto nato all’interno della Biblioteca nazionale centrale di Firenze (BNCF). È un sistema di indicizzazione semantica costituito da regole codificate (inerenti sintassi e terminologia; BNCF 2006) e da un Thesaurus generale. La BNCF ha sempre avuto un ruolo rilevante nell’elaborazione e nell’aggiornamento di strumenti di indicizzazione. L’obiettivo era di rinnovare il precedente strumento, il Soggettario per i cataloghi delle biblioteche italiane (BNCF 1956), e di adeguarlo a principi e standard internazionali alla luce delle esigenze poste dalla nuova generazione di utenti.

Nel 2007 è stato pubblicato il volume contenente le regole di indicizzazione e un prototipo del Thesaurus in continua evoluzione accessibile sul web. Il Thesaurus, ormai lontano dall’essere un prototipo, è accessibile gratuitamente dalle postazioni di ricerca della BNCF e tramite abbonamento dall’esterno, ma da luglio 2010 sarà consultabile liberamente online.[^5]

Il Thesaurus si accresce costantemente grazie al gruppo di lavoro della BNCF e alla collaborazione esterna di alcune istituzioni, iniziata nel 2009.[^6] Dal 2007 la Bibliografia nazionale italiana (BNI), sempre a cura della BNCF, ha iniziato a impiegare il Nuovo soggettario, e gradualmente anche altre biblioteche italiane stanno transitando dal vecchio al nuovo linguaggio.

Il Nuovo soggettario è predisposto per un’indicizzazione pre-coordinata (la BNI utilizza i termini del Thesaurus per la costruzione di stringhe di soggetto), ma può essere usato anche in modalità post-coordinata, come dimostrano alcune esperienze già in atto.[^7]

Le quattro componenti che costituiscono la struttura del sistema sono:

1. il Thesaurus;
2. le Norme per il controllo terminologico e per la costruzione delle stringhe di soggetto;
3. il Manuale applicativo (pubblicato online da febbraio 2010, contenente istruzioni ed esempi applicativi, sia di tipo semantico che sintattico);
4. l’archivio delle stringhe di soggetto derivanti dall’uso del nuovo linguaggio.

L’interfaccia di ricerca del Thesaurus consente di consultare anche la versione digitale del vecchio strumento di indicizzazione (Soggettario del 1956 e suoi aggiornamenti), offrendo quindi un completo accesso a tutto il patrimonio terminologico della tradizione italiana.

Il Thesaurus del Nuovo soggettario è dunque un vocabolario generale che si sta costantemente accrescendo e che attualmente comprende circa 35.000 termini. È generale sia dal punto di vista dei domini coinvolti, sia perché applicabile all’indicizzazione di risorse di varia natura.[^8]

È conforme all’ISO 2788-1986 (International Organization for Standardization 1986) e, in attesa della pubblicazione definitiva del nuovo ISO 25964 che lo sostituirà, sono state considerate anche le indicazioni di ANSI/NISO Z39.19 del 2005 e dello standard britannico BS 8723:2005-2008 (ANSI/NISO 2005; British Standards Institution 2005–2008; cfr. Motta e Tiberi 2009).

Per quanto riguarda le caratteristiche strutturali del vocabolario, si tratta di un Thesaurus prevalentemente monogerarchico (la maggior parte dei termini ha un solo BT). La struttura gerarchica viene costruita applicando l’analisi a faccette e criteri di precedenza definiti. La poligerarchia è adottata solo raramente (secondo criteri espressamente indicati) e comunque sempre nel rispetto dei principi che regolano le relazioni gerarchiche.

L’analisi a faccette assume il ruolo fondamentale di organizzare i termini in una struttura classificatoria basata su quattro categorie principali (Agenti, Azioni, Cose, Tempo) e su ulteriori caratteristiche di divisione (13 faccette: Persone e gruppi, Attività, Processi, Strumenti, ecc.; cfr. Cheti e Paradisi 2008). Come sostiene Vanda Broughton, “l’analisi a faccette rende molto più facile la gestione dell’intera gamma di concetti, compresi quelli relativi a idee astratte. Ad oggi, questo tipo di analisi, intesa come base per la creazione di un insieme integrato di strumenti lessicali, non ha rivali” (2008, 257).

Il sistema del Nuovo soggettario si basa su un modello analitico-sintetico, quindi non enumera a priori tutti i possibili termini e tutte le loro possibili combinazioni all’interno di stringhe di soggetto, ma consente di inserirne di nuovi al bisogno. L’indicizzatore può proporre nuovi termini in fase di catalogazione; ne deriva un sistema aperto, facilmente scalabile e flessibile in fase di indicizzazione.

Si tratta dunque di un Thesaurus che è anche in grado di gestire il passaggio fra vecchie e nuove forme terminologiche, e ha anche la caratteristica di presentare dati che esplicitano all’utente il complesso lavoro di analisi semantica svolto da chi lo allestisce. Uno dei suoi punti di forza è senza dubbio l’ampio apparato di informazioni associato a ogni termine e la presenza di collegamenti a risorse elettroniche esterne.

Come si può vedere nell’esempio del termine “Acculturazione”, i record dei termini prevedono numerose note: note di definizione, note d’ambito, note di orientamento all’interno delle note d’ambito, note storiche (con informazioni su precedenti forme, significati, usi del termine), note sintattiche (note che danno istruzioni all’indicizzatore sull’uso del termine nella costruzione delle stringhe di soggetto).

Nell’interfaccia di ricerca gli utenti possono facilmente individuare, nel campo Fonte, tutte le risorse utilizzate per controllare significati, morfologia e garanzia bibliografica dei termini. Queste fonti repertoriali possono essere liste di intestazioni di soggetto (ad es. LCSH, RAMEAU), thesauri generali e specializzati (ad es. AAT, EUROVOC, MESH), dizionari (ad es. il *Dizionario Treccani* online), enciclopedie (*Enciclopedia Britannica*, *Enciclopedia Italiana Treccani*, ecc.). Se le fonti citate sono disponibili liberamente sul web, è stato inserito un link diretto dal campo Fonte del termine.

Il Thesaurus può essere consultato grazie a un’applicazione che consente la ricerca dei termini, la visualizzazione delle schede, la presentazione dell’intera struttura gerarchica e la navigazione delle relazioni attraverso hyperlink. Questa funzionalità può essere utile nel momento in cui il vocabolario viene utilizzato come strumento per organizzare risorse digitali, e la visualizzazione gerarchica può essere navigata per raggiungere direttamente queste risorse.

Il Thesaurus del Nuovo soggettario ha un’architettura flessibile sotto diversi aspetti, che permette:

1. una costante crescita quantitativa;
2. di accogliere anche pacchetti di terminologia specialistica e settoriale, pur in un contesto che rimane comunque generale;
3. di dialogare e interagire con thesauri specializzati, con altri strumenti di indicizzazione, con strumenti lessicografici ed enciclopedici, attraverso modelli strutturali di vario tipo, come i recenti standard bibliografici hanno delineato.[^9]

## Conversione in SKOS del Thesaurus del Nuovo soggettario

Il Nuovo soggettario si propone dunque come un sistema per l’organizzazione della conoscenza, in cui ogni funzionalità è finalizzata al recupero dell’informazione. L’utilità di questi sistemi per lo sviluppo del web è ormai indiscussa, nonostante in passato linguaggi di questo tipo siano stati considerati molto complessi da costruire e usare. Essendo nati come strumenti biblioteconomici tradizionali, inizialmente sembravano inappropriati per un ambiente digitale e non necessari rispetto a quanto consentito dalla potenza nel processare informazioni dei moderni motori di ricerca. L’esperienza del Nuovo soggettario ha dimostrato che i due mondi possono reciprocamente potenziarsi. Infatti, se da un lato il Thesaurus viene reso disponibile come applicazione web accessibile all’esterno, a sua volta il sistema ha la possibilità di accedere a risorse esterne attraverso il protocollo Zthes (n.d.).

In quest’ottica SKOS nasce come linguaggio comune per vocabolari controllati, come thesauri, schemi di classificazione, tassonomie e soggettari. Non va dimenticato però che SKOS si basa su standard già esistenti: RDF (Resource Description Framework) e RDFS (RDF Schema), che si propongono come linguaggi di interoperabilità più generici. Quindi SKOS si colloca in un contesto di interoperabilità tra vocabolari controllati che si pone in un contesto di interoperabilità ancora più ampio.

Quindi la decisione di sperimentare la conversione del Thesaurus del Nuovo soggettario in SKOS può essere vista come la volontà di compiere un ulteriore passo verso una maggiore interoperabilità con altri sistemi. Questa è la strada intrapresa anche da altri importanti sistemi di indicizzazione: le americane LCSH, il sistema francese RAMEAU, le regole tedesche RSWK, thesauri specialistici come AGROVOC, MESH, e in ambito italiano il thesaurus LIUC dell’Università di Castellanza, ma anche schemi di classificazione come la Classificazione decimale Dewey (DDC), la Classificazione decimale universale (UDC) e la Classificazione Bliss (BC).

RDF, RDFS e SKOS sono linguaggi basati su triple di tipo Soggetto–Predicato–Oggetto, che si basano sui concetti. Tuttavia tra i vocabolari controllati ci sono sia strumenti che sposano l’adozione di termini — come il Nuovo soggettario — sia quella di concetti. Questa caratteristica, che SKOS eredita dai suoi padri (RDF e RDFS), oltre a essere discutibile a livello teorico, può provocare nel processo di conversione una perdita di informazioni (Van Assem et al. 2006), soprattutto nel caso di thesauri multilingui (Ballestra 2008). Per esempio, nell’ambito della traduzione del thesaurus LIUC — il primo thesaurus italiano disponibile sul web a sperimentare la conversione — la scelta di SKOS che un concetto possa essere rappresentato da termini di lingue diverse crea problemi di conversione (Cavaleri 2009).

Come detto in precedenza, il Thesaurus del Nuovo soggettario è basato sullo standard per thesauri monolingui ISO 2788, compatibile con SKOS. Il codice identificativo di ogni termine del Thesaurus è stato usato per generare il codice di identificazione RDF. Questa soluzione è stata scelta anche nella conversione delle LCSH, in cui per identificare i concetti di SKOS è stato usato il numero LCCN (Library of Congress Control Number) che si trova nel campo 001 del linguaggio MARC. Il numero è stato incorporato in un indirizzo URL del tipo `lcsh.info/{lccn}#concept`.

Le relazioni gerarchiche (BT e NT), quelle associative (RT) e di equivalenza (USE/UF) tra i termini del Thesaurus del Nuovo soggettario sono state convertite negli elementi corrispondenti del data model di SKOS: rispettivamente skos:broader, skos:narrower, skos:relatedTerm e skos:altLabel. Sono stati riscontrati dei problemi invece per esprimere due particolari relazioni del Thesaurus, che hanno lo scopo di connettere le precedenti forme terminologiche con le nuove:

1. la relazione di variante storica, una relazione non standard del Thesaurus del Nuovo soggettario che collega termini preferiti del vocabolario a termini del vecchio strumento non più accettati. Il legame espresso con la sigla “Historical see for” (HSF) è di estrema utilità perché consente di caricare in modo automatico nei cataloghi in linea delle biblioteche i legami fra vecchi e nuovi termini, senza correggere ogni singola intestazione di soggetto mutata;
2. la relazione di scomposizione, espressa dal simbolo USE+ e dal suo inverso UF+. Questa relazione collega termini composti a termini preferiti derivati dalla loro scomposizione, e viceversa.

Per risolvere il primo problema (la variante storica) abbiamo pensato di usare una subpropriety dell’etichetta di SKOS hiddenLabel, che viene trasformata in una sottoetichetta del tipo `nuovosoggettario:obsoleteTerm = X` (Van Assem et al. 2006, 7). In questo caso, quindi, bisognerebbe avanzare al W3C una modifica dello standard; altrimenti questa soluzione si tradurrebbe in una mera personalizzazione del linguaggio che gli altri sistemi non riuscirebbero a interpretare, a scapito dell’interoperabilità stessa, il principale obiettivo di SKOS.

Nel secondo caso, invece, abbiamo ipotizzato di usare come riferimento quanto è stato fatto per il Thesaurus MESH. Durante il processo di conversione del MESH, per un problema simile è stata creata ad hoc l’etichetta mesh:preferredCombination (Van Assem et al. 2006, 13); stiamo valutando se usare questa stessa soluzione anche per il Thesaurus del Nuovo soggettario. Per ora la relazione di scomposizione compare come una semplice AltLabel del termine preferito del Thesaurus, con un’evidente perdita di informazioni.

Un caso analogo si è verificato anche durante il passaggio in SKOS di LCSH e di RAMEAU. Le americane LCSH, così come il sistema francese RAMEAU, possono presentare intestazioni di soggetto formate da due concetti composti (per esempio “Teatro — 17. sec.”) che sono stati resi in SKOS uniti con il semplice trattino: ma in questo modo i due termini non vengono interpretati come separati e combinati insieme al momento della costruzione della stringa di soggetto, bensì come un unico concetto composto. Anche in questo esempio, quindi, la struttura estremamente semplificata di SKOS provoca una perdita di informazioni utili.

Come abbiamo visto in precedenza, oltre alle relazioni semantiche, ogni termine del Thesaurus presenta un ricco apparato di informazioni: vari tipi di note, la maggior parte delle quali trovano un’adeguata etichetta in SKOS, per esempio skos:definition, skos:scopeNote, skos:historyNote, skos:editorialNote. Quest’ultima è stata usata, nella nostra sperimentazione, per indicare, anche più volte nello stesso record del termine: il campo dei repertori consultati per il controllo terminologico, il campo per l’agenzia bibliografica che propone il termine, il campo per lo status di lavorazione del termine.

Abbiamo usato l’etichetta skos:example per introdurre la nota sintattica che dà indicazioni per la costruzione delle stringhe di soggetto secondo le regole del sistema di indicizzazione.

Inoltre, molti termini del Thesaurus del Nuovo soggettario sono stati mappati con le corrispettive notazioni della Classificazione decimale Dewey (DDC).[^10] Questo consente di costruire un ponte verso altri sistemi che, pur basandosi su diversi metodi di indicizzazione per soggetto o su diverse lingue, si affiancano all’uso della DDC e ne prevedono il collegamento. Questo mapping è stato mantenuto anche nel passaggio del Thesaurus in SKOS usando l’etichetta skos:notation.

Caratteristica interessante di SKOS è la sua interoperabilità con altri schemi di metadati come Dublin Core e FOAF (Friend of a Friend). Nel Thesaurus del Nuovo soggettario abbiamo usato, per alcune informazioni di servizio come la data di creazione del termine, lo schema Dublin Core.

## Conclusioni

Che possibilità apre per il Thesaurus del Nuovo soggettario la conversione in SKOS? I benefici più immediati sono senza dubbio:

1. la maggiore interoperabilità con altri sistemi che sono stati convertiti in SKOS;
2. il vantaggio di avere ogni concetto/termine del Thesaurus identificato unicamente da un URI.

La conversione in SKOS dei vocabolari controllati usati per l’indicizzazione per soggetto in ambito bibliotecario può essere usata come base per la mappatura semantica di sistemi di organizzazione della conoscenza che strutturano domini disciplinari differenti o che usano lingue diverse. Quindi l’interoperabilità tecnica diviene la base per l’interoperabilità semantica fra i vari strumenti.

In quest’ottica il Nuovo soggettario ha la possibilità di allinearsi con progetti in campo europeo di condivisione di accessi semantici come il progetto MACS (n.d.), che ha lo scopo di sviluppare un sistema per l’accesso multilingue per soggetto tramite la mappatura semantica dei sistemi d’indicizzazione RAMEAU (per la lingua francese), LCSH (per la lingua inglese) e SWD (per la lingua tedesca), che hanno tutti una versione in SKOS. Entrare a far parte del progetto MACS vuol dire ricoprire un ruolo importante anche nell’arricchimento del recupero semantico di Europeana (European digital library, museum and archive) attraverso il progetto TELPlus (n.d.), che ha ripreso i risultati di MACS in questo ambito.

A livello italiano, il Thesaurus del Nuovo soggettario potrebbe proporsi anche come vocabolario controllato di riferimento per il controllo di uniformità e l’organizzazione dei contenuti nei siti web della Pubblica amministrazione. La recente pubblicazione, in versione draft, delle nuove Linee guida per i siti web della PA (Ministero per la Pubblica Amministrazione e l’Innovazione 2010) prevede infatti che “i sistemi di classificazione utilizzati per le risorse dei siti web della Pubblica amministrazione debbano consentire l’interoperabilità semantica, ovvero la possibilità di individuare in modo omogeneo gli attributi che caratterizzano una risorsa (metadati) e i valori che gli attributi possono assumere (vocabolari) quando si descrivono i contenuti. Sistemi tecnologicamente interoperabili in assenza di interoperabilità semantica non possono scambiare e condividere dati, documentazione e servizi” (2010).

Il Thesaurus del Nuovo soggettario potrebbe diventare un “servizio terminologico” da affiancare e integrare con quelli già in uso nei siti degli enti della Pubblica amministrazione, anche grazie alla partecipazione attiva degli stessi enti interessati, che potrebbero proporre nuovi termini. In questo modo tutti i siti pubblici offrirebbero una modalità di accesso semantico comune, attraverso lo stesso linguaggio condiviso, con un evidente vantaggio per l’usabilità stessa dei siti e, eventualmente, il controllo su ulteriori tag proposti dagli stessi utenti, validati da chi allestisce il Thesaurus.

## Bibliografia

- American National Standards Institute – National Information Standards Organization (ANSI/NISO). 2005. *Z39.19-2005: Guidelines for the Construction, Format, and Management of Monolingual Controlled Vocabularies*. Bethesda: NISO Press.
- Ballestra, Laura. 2008. “Multiculturalità e thesauri multilingue: problemi e prospettive alla luce delle Guidelines for Multilingual Thesauri di IFLA.” Intervento all’11° Workshop Teca del Mediterraneo. [www.bcr.puglia.it/tdm/documenti/workshop/2008/Ballestra.pdf](http://www.bcr.puglia.it/tdm/documenti/workshop/2008/Ballestra.pdf).
- Biblioteca Nazionale Centrale di Firenze (BNCF). 1956. *Soggettario per i cataloghi delle biblioteche italiane*. Firenze: Stamperia Il Cenacolo.
- ———. 2006. *Nuovo soggettario: Guida al sistema italiano di indicizzazione per soggetto. Prototipo del Thesaurus*. Milano: Editrice Bibliografica.
- British Standards Institution (BSI). 2005–2008. *BS 8723: Structured Vocabularies for Information Retrieval*. London: British Standards Institution.
- Broughton, Vanda. 2008. *Costruire thesauri: Strumenti per indicizzazione e metadati semantici*. A cura di Piero Cavaleri, Laura Ballestra e Luisa Venuti. Milano: Editrice Bibliografica.
- Cavaleri, Piero. 2009. “Il thesauro di economia e scienze sociali della Biblioteca Rostoni e SKOS.” Intervento al convegno “I thesauri tra cataloghi e Web,” Firenze, Istituto degli Innocenti, 6 febbraio. [www.iskoi.org/doc/thesauri4.htm](http://www.iskoi.org/doc/thesauri4.htm).
- Cheti, Alberto, e Federica Paradisi. 2008. “Facet Analysis in the Development of a General Controlled Vocabulary.” *Axiomathes* 18 (2): 223–241.
- International Organization for Standardization (ISO). 1986. *ISO 2788: Documentation — Guidelines for the Establishment and Development of Monolingual Thesauri*. Geneva: ISO.
- Lucarelli, Anna. 2008. “Quando una collezione speciale chiede ospitalità ad una grande biblioteca.” In *Piccoli scritti di biblioteconomia per Luigi Crocetti: 10 marzo 2007–10 marzo 2008*, a cura di Carmela Cavallaro e Perla Innocenti, 183–201. Manziana: Vecchiarelli.
- Ministero per la Pubblica Amministrazione e l’Innovazione. 2010. *Linee guida per i siti web della PA*. [www.innovazionepa.gov.it](http://www.innovazionepa.gov.it/media/367125/linee_guida_siti_web_pa.pdf) ([archiviato](https://web.archive.org/web/20110908003222/http://www.innovazionepa.gov.it/media/367125/linee_guida_siti_web_pa.pdf)).
- Motta, Marta, e Melissa Tiberi. 2009. “Riflessi dello standard britannico BS 8723 nel Thesaurus del Nuovo soggettario.” *Bollettino AIB* 49 (3): 325–340.
- “Multilingual Access to Subjects (MACS).” n.d. [macs.vub.ac.be/pub](https://macs.vub.ac.be/pub) ([archiviato](https://web.archive.org/web/20070613072941/https://macs.vub.ac.be/pub/)).
- Svenonius, Elaine. 2000. *The Intellectual Foundation of Information Organization*. Cambridge, MA: MIT Press.
- “TELplus.” n.d. [www.theeuropeanlibrary.org](http://www.theeuropeanlibrary.org/portal/organisation/cooperation/telplus/index.php).
- Van Assem, Mark, Véronique Malaisé, Alistair Miles, e Guus Schreiber. 2006. “A Method to Convert Thesauri to SKOS.” [www.cs.vu.nl](http://www.cs.vu.nl/~mark/papers/Assem06b.pdf) ([archiviato](https://web.archive.org/web/20070125043216/http://www.cs.vu.nl/~mark/papers/Assem06b.pdf)).
- “Zthes.” n.d. [zthes.z3950.org](http://zthes.z3950.org/).

[^1]: LCSH (Library of Congress Subject Headings) è il repertorio delle voci di soggetto utilizzate dalla Library of Congress a partire dal 1898.
[^2]: RAMEAU (Répertoire d’autorité-matière encyclopédique et alphabétique unifié) è la lista controllata delle voci di soggetto assegnate dal 1980 ai record bibliografici inseriti nel catalogo in linea della Bibliothèque nationale de France, integrata con voci proposte da biblioteche universitarie, di pubblica lettura e di ricerca. Le voci di RAMEAU derivano in massima parte dal *Répertoire de vedettes-matière*, elaborato dalla biblioteca dell’Université de Laval (Québec) sulla base delle LCSH.
[^3]: LIUC è il thesaurus di economia e scienze sociali dell’Università Carlo Cattaneo di Castellanza.
[^4]: MESH (Medical Subject Headings) è il thesaurus usato per indicizzare gli articoli delle oltre 5.000 riviste mediche presenti nel database bibliografico Medline/PubMed.
[^5]: Il Thesaurus è raggiungibile all’indirizzo [www.edigeo-online.it/Nuovo_soggettario](http://www.edigeo-online.it/Nuovo_soggettario/#?rigamenu=Nuovosoggettario.Thesaurus) ([archiviato](https://web.archive.org/web/20110928151326/http://www.edigeo-online.it/Nuovo_soggettario/)).
[^6]: Le istituzioni che finora collaborano al progetto sono: Biblioteca dell’Università Bocconi di Milano, Università degli Studi di Milano, l’Università di Pisa (Area bibliotecaria, archivistica e museale), Biblioteca Mario Rostoni dell’Università Carlo Cattaneo di Castellanza (LIUC), l’Istituto di teorie e tecniche dell’informazione giuridica (ITTIG) del Consiglio nazionale delle ricerche (CNR), il Coordinamento biblioteche speciali e specialistiche di Torino (CoBiS) e la Società IDEST.
[^7]: La società IDEST, che cura la serie speciale della Bibliografia nazionale dei libri per ragazzi, utilizza i termini del Thesaurus per accessi da semplici parole chiave.
[^8]: Presso la Biblioteca nazionale di Firenze, il Nuovo soggettario è stato applicato con successo per indicizzare fotografie di un prestigioso fondo del Novecento (Fondo Pannunzio). Cfr. Lucarelli (2008).
[^9]: Cfr. i modelli *Backbone structure* e *Satellite vocabularies* descritti rispettivamente in British Standards Institution (2005–2008) e ANSI/NISO Z39.19 (2005). “Il Thesaurus del Nuovo soggettario può proporsi come una sorta di meta-thesaurus da cui possono derivare tanti altri thesauri specialistici, oppure definirsi come punto di scambio e raccordo fra molteplici thesauri specializzati in varie discipline” (Motta e Tiberi 2009).
[^10]: È allo studio la fattibilità di una versione italiana di WebDewey ([www.oclc.org/dewey/versions/webdewey](http://www.oclc.org/dewey/versions/webdewey)), anche al fine di creare un’interoperabilità effettiva e non solo virtuale tra il Thesaurus del Nuovo soggettario e la CDD.
