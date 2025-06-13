<template>
  <div class="container my-3">
    <div class="row">
      <div class="col-sm-12">
        <h2>Guida utente</h2>
        <p>
          Flash offre due esperienze distinte a seconda che tu abbia effettuato l'accesso come
          utente o meno (“ospite”).
        </p>
        <p>
          Le pagine ospite sono facilmente riconoscibili dal colore grigio dell'intestazione:
          <img src="/images/gray.png" alt="colore grigio" />
        </p>
        <p>
          Dopo aver effettuato l'accesso, il colore dell'intestazione diventa
          <a target="_blank" href="https://www.pantone.com/eu/it/color-of-the-year/2025"
            >Mocha Mousse</a
          >
          “scuro”: <img src="/images/dark_mocha_mousse.png" alt="Mocha Mousse scuro" />
        </p>
        <h3 id="utente-ospite">Utente ospite</h3>
        <p>
          L'aggregatore presenta all'utente ospite un elenco limitato di notizie (solo gli articoli
          già letti dagli utenti registrati):
        </p>
        <p><img src="/images/homepage.jpeg" alt="Home page" /></p>
        <p>Cliccando su un articolo si apre una pagina interstiziale:</p>
        <p>
          <img src="/images/article_detail.jpeg" alt="Dettagli dell'articolo" />
        </p>
        <p>che invita l'utente a effettuare il login per leggere il testo completo.</p>
        <h3 id="utente-registrato">Utente registrato</h3>
        <p>
          Una volta effettuato l'accesso, agli utenti viene presentata un'altra visualizzazione.
        </p>
        <p>
          La homepage presenta un layout a schede per navigare tra le diverse visualizzazioni degli
          articoli:
        </p>
        <p><img src="/images/res_homepage.jpeg" alt="Restricted access home page" /></p>
        <p>Le visualizzazioni disponibili sono:</p>
        <ul>
          <li>
            <strong>Tutti</strong> (Tutti gli articoli): mostra tutti gli articoli disponibili,
            paginati e opzionalmente filtrati (per lingua, data, lunghezza e ricerca a tutto testo,
            vedi dettaglio Funzioni 1 sotto).
          </li>
          <li>
            <strong>Letti</strong> (Articoli letti): mostra gli articoli che to e/o altri hanno già
            letto, paginati.
          </li>
          <li>
            <strong>Per te</strong> (Feed personalizzato): il tuo feed algoritmico, personalizzato
            in base alle tue preferenze e alle valutazioni dei feed (vedi dettaglio Funzioni 5
            sotto).
          </li>
          <li>
            <strong>Preferiti</strong> (Preferiti): mostra gli articoli dei tuoi feed preferiti,
            paginati.
          </li>
        </ul>
        <p>
          Gli articoli all'interno di queste visualizzazioni a schede sono visualizzati come schede,
          che mostrano:
        </p>
        <ul>
          <li>Il logo del feed (collegato alla pagina/fonte del feed).</li>
          <li>
            Il titolo dell'articolo. Se l'articolo è stato tradotto, potrebbero essere visualizzati
            sia il titolo originale che quello tradotto.
          </li>
          <li>Un breve estratto del contenuto dell'articolo.</li>
          <li>
            Il nome dell'autore (collegato a una pagina che mostra altri articoli dello stesso
            autore).
          </li>
          <li>
            L'ora di pubblicazione, visualizzata come tempo relativo (ad esempio, “2 ore fa”).
          </li>
          <li>Il tempo di lettura stimato per l'articolo.</li>
        </ul>
        <p>
          Gli elenchi di tutti gli articoli, gli articoli letti e gli articoli preferiti sono
          paginati ed è possibile caricare altri articoli utilizzando il pulsante “Carica altri
          articoli”.
        </p>
        <p>Cliccando su un articolo qualsiasi si accede alla pagina dei dettagli dell'articolo:</p>
        <p>
          <img src="/images/res_article_detail.jpeg" alt="Dettagli dell'articolo riservato" />
        </p>
        <p>
          che mostra il testo completo (se disponibile), la traduzione opzionale e gli articoli
          correlati.
        </p>
        <h3 id="funzionalità">Funzioni</h3>
        <ol>
          <li>
            <p>
              <strong>Filtraggio</strong> – dall'elenco principale degli articoli (ad esempio,
              “Tutti”) nella home page, clicca sul pulsante “filtro” (un pulsante mobile con l'icona
              di un imbuto, situato sul lato destro dello schermo) per espandere una barra laterale
              fuori dallo schermo. Questa barra laterale offre diversi criteri di filtraggio lato
              client: per lingua, data e lunghezza. Man mano che i criteri di filtraggio vengono
              modificati, l'elenco degli articoli viene aggiornato (quasi) in tempo reale. È
              disponibile anche la ricerca a tutto testi, che avviene sul lato server: una volta
              inserite due o più parole chiave, mentre si attende il caricamento dei dati aggiornati
              dal backend, viene visualizzato un indicatore di caricamento con un promemoria che
              ricorda che l'elenco corrente è filtrato. Tutte le impostazioni di filtraggio vengono
              mantenute sul dispositivo, il che significa che se si utilizza Flash da due
              dispositivi, è possibile visualizzare feed di notizie diversi in base alle
              impostazioni di filtro locali.
            </p>
          </li>
          <li>
            <p>
              <strong>Condivisione</strong> sui social media: dalla pagina dei dettagli
              dell'articolo, clicca sull'icona “condividi” e apri il link all'articolo sul tuo
              social network preferito (Bluesky, Facebook, Linkedin, Mastodon, Reddit, Telegram,
              Twitter e Whatsapp). Per Mastodon, la prima volta che condividi un articolo ti verrà
              chiesto di selezionare la tua istanza (questa impostazione viene salvata sul
              dispositivo). Infine, hai anche l'opzione “Copia link negli appunti” per la
              condivisione su altre app come SMS ed e-mail.
            </p>
          </li>
          <li>
            <p>
              Salvataggio di articoli in <strong>elenchi</strong>: puoi creare uno o più elenchi,
              quindi salvare gli articoli per leggerli in un secondo momento, aggiungerli ai
              segnalibri ed esportarli. Questi sono gestiti dalla pagina “Articoli salvati” (icona a
              forma di cuore).
            </p>
          </li>
          <li>
            <p>
              <strong>Somiglianza</strong> degli articoli: il titolo e il contenuto di ogni articolo
              vengono utilizzati per calcolare la somiglianza. Ciò consente di suggerire articoli
              correlati (questi vengono mostrati sotto i contenuti nella pagina dei dettagli degli
              articoli) e di generare un newsfeed personalizzato (vedi punto successivo).
            </p>
          </li>
          <li>
            <p>
              <strong>Newsfeed algoritmico</strong>: la scheda “Per te” (Newsfeed personalizzato)
              della homepage mostra un elenco di articoli aggiornato automaticamente ogni ora da un
              algoritmo basato sulle tue preferenze. Le opzioni di personalizzazione del newsfeed
              sono impostate dalla pagina “Impostazioni”: lingue e parole chiave nella
              whitelist/blacklist. L'algoritmo si basa sulla somiglianza tra l'articolo e le parole
              nella whitelist.
            </p>
          </li>
          <li>
            <p>
              <strong>Feed preferiti</strong>: la scheda “Preferiti” della homepage mostra gli
              articoli dei feed che sono stati contrassegnati come preferiti (icona a forma di
              cuore) nella pagina “Feed”.
            </p>
          </li>
          <li>
            <p>
              <strong>Feed esclusi</strong> – i feed contrassegnati come nascosti (icona occhio
              barrato) nella pagina “Feed” non vengono mai visualizzati nell'elenco principale degli
              articoli (ad es. “Tutti”) nella home page.
            </p>
          </li>
          <li>
            <p>
              <strong>TTS</strong> (text-to-speech) – la piattaforma Flash può leggere ad alta voce
              singoli articoli o tutti gli articoli presenti in un elenco (manuale o automatico),
              utilizzando le voci locali presenti sul dispositivo. Ciò potrebbe essere utile per
              l'accessibilità o per creare una sorta di “podcast sintetico”. Durante la lettura
              degli articoli, uno sfondo grigio chiaro mostra lo stato di avanzamento. Una piccola
              barra degli strumenti verde fluttuante nella parte inferiore consente di mettere in
              pausa, saltare avanti e indietro e interrompere completamente la lettura. Nota:
              affinché funzioni, è necessario installare le voci locali (non funziona bene con le
              voci “cloud”) e disattivare il blocco automatico dello schermo (altrimenti la lettura
              si interrompe bruscamente quando lo schermo si blocca).
            </p>
          </li>
          <li>
            <p>
              <strong>Traduzioni automatiche</strong>: dalla pagina dei dettagli dell'articolo, gli
              utenti registrati hanno accesso a un pulsante “Traduci” che richiede le traduzioni del
              titolo e del contenuto da un servizio nel cloud (attualmente Microsoft Translator).
              L'indicatore inizia a girare, poi dopo pochi secondi, se la richiesta ha esito
              positivo, l'articolo riappare, questa volta con il testo nella lingua originale
              affiancato alla traduzione in italiano (o, su schermi stretti, uno dopo l'altro). La
              funzione è disponibile solo per gli articoli in una lingua diversa dalla lingua di
              base dell'istanza, che per l'istanza attualmente attiva notizie.calomelano.it è
              l'italiano.
            </p>
          </li>
          <li>
            <p>
              <strong>Scaricare</strong> articoli – i singoli articoli o tutti gli articoli di un
              elenco (manuale o automatico) possono essere esportati nei formati HTML, PDF (in
              formato A5) ed EPUB. Ciò è utile per inviare una copia a un amico o per leggere
              articoli lunghi sul proprio lettore di ebook.
            </p>
          </li>
          <li>
            <p>
              <strong>Mastodon Bot</strong> – Flash può pubblicare automaticamente i nuovi articoli
              dal newsfeed di un utente su un account Mastodon specificato. Per abilitare questa
              funzione per un utente:
            </p>
            <ul>
              <li>Accedi al profilo dell'utente nell'interfaccia di amministrazione di Django.</li>
              <li>Seleziona il flag <code>È utente bot</code>.</li>
              <li>
                Inserisci il nome dell'elenco degli articoli dell'utente che devono essere
                pubblicati. Se desideri pubblicare il newsfeed automatico “Per te”, impostalo su
                <code>newsfeed</code>.
              </li>
              <li>
                Inserisci le credenziali API di Mastodon (in Mastodon, vai su Preferenze account ->
                Sviluppo -> Nuova applicazione, crea una nuova applicazione, inserisci Nome e Sito
                web, con gli ambiti
                <code>read</code>, <code>profile</code> e <code>write:statuses</code>):
                <ul>
                  <li><code>ID client Mastodon</code></li>
                  <li><code>Segreto client Mastodon</code></li>
                  <li><code>Token di accesso Mastodon</code></li>
                  <li>
                    <code>URL base API Mastodon</code> (ad es.
                    <code>https://mastodon.social</code> o l'URL della tua istanza)
                  </li>
                </ul>
              </li>
            </ul>
            <br />
            <p>Funzionamento del bot:</p>
            <ul>
              <li>Il bot viene eseguito automaticamente ogni ora.</li>
              <li>
                Esegue la scansione dell'elenco di articoli selezionati dell'utente bot configurato
                alla ricerca di nuovi articoli (non letti).
              </li>
              <li>
                I nuovi articoli trovati vengono pubblicati sull'account Mastodon associato alle
                credenziali fornite.
              </li>
              <li>
                Dopo aver pubblicato con successo un articolo, questo viene contrassegnato come
                “letto” dall'utente bot per evitare che venga ripubblicato.
              </li>
              <li>Per evitare lo spamming, il bot pubblicherà un massimo di 5 articoli all'ora.</li>
            </ul>
            <br />
          </li>
          <li>
            <p>
              <strong>Esportazione OPML</strong>: esporta il file
              <a href="https://en.wikipedia.org/wiki/OPML" target="_blank"
                >OPML (Outline Processor Markup Language)</a
              >
              contenente l'elenco dei feed aggregati dall'URL pubblico
              <code>/api/feeds/opml/</code>. Questo file può essere importato in altri lettori RSS o
              aggregatori.
            </p>
          </li>
        </ol>
      </div>
    </div>
  </div>
</template>
