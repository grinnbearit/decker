(ns decker.core
  (:require [clojure.java.io :as io]
            [clojure.edn :as edn]))


(defn !read-card-lists
  "Reads the list of decks in data/{set}.edn"
  [edition]
  (with-open [f (io/reader (format "data/%s.edn" edition))]
    (edn/read (java.io.PushbackReader. f))))


(defn list-missing-cards
  "Given a cardex and card-list returns a list of missing card names"
  [cardex card-list]
  (for [row (:card-list/cards card-list)
        :when (nil? (cardex (:name row)))]
    (:name row)))


(defn card-list->deck
  "Given an eddex and cardex, converts a card-list to a deck"
  [eddex cardex card-list]
  {:pre [(empty? (list-missing-cards cardex card-list))]}
  #:deck{:name (:card-list/name card-list)
         :description (:card-list/description card-list)
         :decklines
         (for [row (:card-list/cards card-list)
               :let [cardex-row (cardex (:name row))
                     collector-numbers (:cardex/collector-numbers cardex-row)]
               [collector-number copies] (frequencies (take (:count row) (cycle collector-numbers)))]
           #:deckline{:card (get-in eddex [(:cardex/code cardex-row) collector-number])
                      :count copies})})


(defn highres-deck?
  "Given a deck, returns if all cards have highres prints"
  [deck]
  (->> (:deck/decklines deck)
       (every? (comp :card/highres? :deckline/card))))


(defn deck->editions
  "Given a deck, returns a set of all editions that the cards are from"
  [deck]
  (->> (:deck/decklines deck)
       (map (comp :card/code :deckline/card))
       (into #{})))


(defn deck->count
  "Given a deck, returns the number of cards in the deck"
  [deck]
  (->> (:deck/decklines deck)
       (map :deckline/count)
       (apply +)))
