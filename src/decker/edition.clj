(ns decker.edition
  (:require [clj-http.client :as client]
            [clojure.pprint :as pprint]
            [net.cgrand.enlive-html :as html]
            [clojure.string :as str]
            [clojure.instant :as inst]
            [clojure.java.io :as io]
            [clojure.edn :as edn]
            [clojure.set :as set]))


(defn !fetch-edition-list
  "returns a list of editions found at https://scryfall.com/sets"
  []
  (let [content (html/html-resource (java.net.URL. "https://scryfall.com/sets"))]
    (for [row (html/select content [:table.checklist :> :tbody :tr])
          :when (= (first (html/select row [:a.pillbox-item html/text])) "en")
          :let [[edition-name _ edition-code _ cardinality date] (->> (drop 1 (html/select row [:td :a html/text]))
                                                                      (drop-while map?))]]
      #:edition{:date (inst/read-instant-date date)
                :code edition-code
                :name (str/trim edition-name)})))


(defn write-edition-list!
  "Writes a list of editions to metadata/editions.edn"
  [edition-list]
  (with-open [f (io/writer "metadata/editions.edn")]
    (binding [*out* f]
      (pprint/pprint edition-list))))


(defn !read-edition-list
  "Reads the current list of editions from metadata/editions.edn

  If the file doesn't exist, returns ()"
  []
  (with-open [f (io/reader "metadata/editions.edn")]
    (edn/read (java.io.PushbackReader. f))))


(defn scryfall->card
  "Converts a standard scyfall card map to a card object"
  [scryfall-card]
  (let [base-card #:card{:code (scryfall-card :set)
                         :collector-number (scryfall-card :collector_number)
                         :name (scryfall-card :name)
                         :layout (scryfall-card :layout)
                         :highres? (scryfall-card :highres_image)}]
    (case (:layout scryfall-card)

      ("normal" "token" "emblem" "planar" "leveler" "scheme"
       "vanguard" "host" "augment" "saga" "class" "meld")
      (assoc base-card
             :card/layout-category :normal
             :card/png (get-in scryfall-card [:image_uris :png])
             :card/type-line (scryfall-card :type_line)
             :card/oracle-text (scryfall-card :oracle_text))

      ("split" "flip" "adventure")
      (assoc base-card
             :card/layout-category :split
             :card/png (get-in scryfall-card [:image_uris :png])
             :card/faces (vec
                          (for [face [0 1]]
                            {:type-line (get-in scryfall-card [:card_faces face :type_line])
                             :oracle-text (get-in scryfall-card [:card_faces face :oracle_text])})))

      ("transform" "double_faced_token" "modal_dfc" "art_series" "reversible_card")
      (assoc base-card
             :card/layout-category :transform
             :card/faces (vec
                          (for [face [0 1]]
                            {:png (get-in scryfall-card [:card_faces face :image_uris :png])
                             :type-line (get-in scryfall-card [:card_faces face :type_line])
                             :oracle-text (get-in scryfall-card [:card_faces face :oracle_text])})))

      (throw (ex-info "unknown layout" {:scryfall-card scryfall-card})))))


(defn !fetch-edition
  "Given the 3 letter code for a edition, returns a list of card metadata from scryfall"
  [edition]
  (loop [acc [] page 1 has-more? true]
    (if (not has-more?)
      (->> (apply concat acc)
           (map scryfall->card))
      (let [response (client/get "https://api.scryfall.com/cards/search"
                                 {:query-params {"order" "set"
                                                 "q" (format "e:%s unique:prints" edition)
                                                 "page" page}
                                  :as :json})]
        (Thread/sleep 50)
        (recur (conj acc (get-in response [:body :data]))
               (inc page)
               (get-in response [:body :has_more]))))))


(defn write-edition!
  "writes edition metadata to a file named metadata/{edition}_metadata.edn
  assumes all cards are from the same edition"
  [card-list]
  (let [edition (-> card-list first :card/code)
        filename (format "metadata/%s_metadata.edn" edition)]
    (with-open [f (io/writer filename)]
      (binding [*out* f]
        (pprint/pprint card-list)))))


(defn !read-edition
  "returns a list of card metadata for the passed edition"
  [edition]
  (let [filename (format "metadata/%s_metadata.edn" edition)]
    (with-open [f (io/reader filename)]
      (edn/read (java.io.PushbackReader. f)))))


(defn !read-edition-cards
  "returns a list of  cards for all editions, in order from newest to oldest"
  []
  (for [{code :edition/code} (!read-edition-list)]
    #:edition-cards{:code code
                    :cards (!read-edition code)}))


(defn !read-eddex
  "returns a map of edition -> collector-number -> card"
  []
  (letfn [(reducer [acc [code card]]
            (assoc-in acc [code (:card/collector-number card)] card))]

    (->> (for [{code :edition/code} (!read-edition-list)
               card (!read-edition code)]
           [code card])
         (reduce reducer {}))))


(def CORE-EDITIONS
  #{"LEA" "LEB" "2ED" "ARN" "ATQ" "3ED" "DRK" "FEM" "4ED" "ICE" "HML" "ALL" "MIR" "VIS" "5ED" "WTH" "TMP"
    "STH" "EXD" "USG" "ULG" "6ED" "UDS" "MMQ" "NEM" "PCY" "INV" "PLS" "7ED" "APC" "ODY" "TOR" "JUD" "ONS"
    "LGN" "SCG" "8ED" "MRD" "DST" "5DN" "CHK" "BOK" "SOK" "9ED" "RAV" "GPT" "DIS" "CSP" "TSP" "PLC" "FUT"
    "10E" "LRW" "MOR" "SHM" "EVE" "ALA" "CON" "ARB" "M10" "ZEN" "WWK" "ROE" "M11" "SOM" "MBS" "NPH" "M12"
    "ISD" "DKA" "AVR" "M13" "RTR" "GTC" "DGM" "M14" "THS" "BNG" "JOU" "M15" "KTK" "FRF" "DTK" "ORI" "BFZ"
    "OGW" "SOI" "EMN" "KLD" "AER" "AKH" "HOU" "XLN" "RIX" "DOM" "M19" "GRN" "RNA" "WAR" "M20" "ELD" "THB"
    "IKO" "M21" "ZNR" "KHM" "STX" "AFR" "MID" "VOW" "NEO" "SNC"})


(defn peripheral-editions
  "returns a set of peripheral (non core) editions from the passed eddex"
  [eddex]
  (set/difference (set (keys eddex)) CORE-EDITIONS))
