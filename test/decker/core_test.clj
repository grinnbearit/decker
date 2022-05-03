(ns decker.codex-test
  (:use midje.sweet
        decker.core)
  (:require [decker.codex :as dx]))


(facts
 "missing cards"

 (missing-cards
  {"card-1" #:cardex{:code "SET-1"
                     :collector-numbers ["1", "2", "3"]}
   "card-2" #:cardex{:code "SET-2"
                     :collector-numbers ["4"]}}

  #:card-list{:name "deck-1"
              :description "description-1"
              :cards [{:count 4, :name "card-1"}
                      {:count 4, :name "card-2"}]})
 => ()

 (missing-cards
  {}
  #:card-list{:name "deck-1"
              :description "description-1"
              :cards [{:count 4, :name "card-1"}
                      {:count 4, :name "card-2"}]})
 => ["card-1" "card-2"])


(facts
 "card-list->deck"

 (card-list->deck

  {"card-1" #:cardex{:code "SET-1"
                     :collector-numbers ["1", "2", "3"]}
   "card-2" #:cardex{:code "SET-2"
                     :collector-numbers ["4"]}}

  #:card-list{:name "deck-1"
              :description "description-1"
              :cards [{:count 4, :name "card-1"}
                      {:count 4, :name "card-2"}]})
 => #:deck{:name "deck-1"
           :description "description-1"
           :decklines [{:deckline/code "SET-1"
                        :deckline/collector-number "1"
                        :deckline/count 2
                        :deckline/name "card-1"}
                       {:deckline/code "SET-1"
                        :deckline/collector-number "2"
                        :deckline/count 1
                        :deckline/name "card-1"}
                       {:deckline/code "SET-1"
                        :deckline/collector-number "3"
                        :deckline/count 1
                        :deckline/name "card-1"}
                       {:deckline/code "SET-2"
                        :deckline/collector-number "4"
                        :deckline/count 4
                        :deckline/name "card-2"}]}

 (card-list->deck
  {}
  #:card-list{:name "deck-1"
              :description "description-1"
              :cards [{:count 4, :name "card-1"}
                      {:count 4, :name "card-2"}]})
 => (throws AssertionError))
