(ns decker.core
  (:require [clojure.java.io :as io]
            [clojure.edn :as edn]
            [decker.codex :as dx]))


(defn !read-card-list
  "Reads the list of decks in data/{set}.edn"
  [edition]
  (with-open [f (io/reader (format "data/%s.edn" edition))]
    (edn/read (java.io.PushbackReader. f))))


(defn card-list->deck
  [edition-cards card-list & {:keys [newest oldest ignore] :as opts}]
  (let [cardex (dx/gen-cardex edition-cards opts)]
    #:deck{:name (:card-list/name card-list)
           :decklines
           (for [row (:card-list/cards card-list)
                 :let [cardex-row (cardex (:name row))
                       collector-numbers (:cardex/collector-numbers cardex-row)]
                 [collector-number copies] (frequencies (take (:count row) (cycle collector-numbers)))]
             #:deckline{:name (:name row)
                        :code (:cardex/code cardex-row)
                        :collector-number collector-number
                        :count copies})}))
