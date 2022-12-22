# NI-DSV-Ring-Final

- As-Far-As-Possible LE Algorithm 


## Specifikace požadavků na semestrální práci
Pro řešení je vyžadováno použití frameworku gRPC od společnosti Google. Úvod do gRPC lze nalézt zde. Zvolený programovací jazyk pro implementaci závisí čistě na autorovi.

Řešení lze implementovat na jediném virtuálním počítači pomocí procesů/vláken, ale tyto procesy/threa/vlákna spolu musí komunikovat prostřednictvím gRPC.

Řešení bude obsahovat počáteční proces/vlákno, který spustí všechny komunikující procesy/vlákna.

Při spuštění programu bude z příkazového řádku předán jeden parametr řetězcové hodnoty představující kruhovou topologii uzlů s jejich ID.

Textový soubor obsahující předem vygenerované kruhové topologie lze stáhnout zde.

Simulace algoritmu musí obsahovat log soubor obsahující přehled odeslaných a přijatých zpráv. Formát zprávy by měl být <Node ID, Time, Sender ID, Receiver ID>. Node ID je ID uzlu, který zprávu zaznamenává, časovou hodnotou se rozumí systémový (procesní) čas bezprostředně před odesláním zprávy nebo po jejím přijetí, Sender ID je uzlu, který zprávu posílá a Receiver ID je ID uzlu, který zprávu obdrží.

Např. zpráva <24, 10:00:00, 11, 24> znamená, že byla přijata a zaznamenána uzlem 24 v čase 10:00:00. Zpráva <24, 10:00:05, 24, 22> znamená, že byla zaznamenána uzlem 24 a odeslána z uzlu 24 do uzlu 22 v čase 10:00:05 atd.

Implementace musí být průběžně ukládána na repozitář FIT’s Giltab z důvodu kontroly změn.

Povinnou součástí projektu je Projektová zpráva obsahující popis algoritmu (vlastními slovy), popis implementace (hlavní třídy, schéma UML atd.) a měření počtu zpráv pro minimálně 100 topologií zde. 

Měření bude obsahovat počet zpráv, které bylo nutné rozšířit kruhovou topologií k dosažení konečného stavu.Projektová zpráva musí být rovněž uložena v úložišti Gitlab.
