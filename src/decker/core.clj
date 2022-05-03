(ns decker.core
  (:require [clojure.java.io :as io]
            [clojure.edn :as edn]))


(defn !read-card-list
  "Reads the list of decks in data/{set}.edn"
  [edition]
  (with-open [f (io/reader (format "data/%s.edn" edition))]
    (edn/read (java.io.PushbackReader. f))))


(defn missing-cards
  "Given a cardex and card-list returns a list of missing card names"
  [cardex card-list]
  (for [row (:card-list/cards card-list)
        :when (nil? (cardex (:name row)))]
    (:name row)))


(defn card-list->deck
  "Given a cardex, converts a card-list to a deck"
  [cardex card-list]
  {:pre [(empty? (missing-cards cardex card-list))]}
  #:deck{:name (:card-list/name card-list)
         :description (:card-list/description card-list)
         :decklines
         (for [row (:card-list/cards card-list)
               :let [cardex-row (cardex (:name row))
                     collector-numbers (:cardex/collector-numbers cardex-row)]
               [collector-number copies] (frequencies (take (:count row) (cycle collector-numbers)))]
           #:deckline{:name (:name row)
                      :code (:cardex/code cardex-row)
                      :collector-number collector-number
                      :count copies})})
