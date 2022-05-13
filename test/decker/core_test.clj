(ns decker.codex-test
  (:use midje.sweet
        decker.core)
  (:require [decker.codex :as dx]))


(facts
 "list missing cards"

 (list-missing-cards
  {"card-1" #:cardex{:code "SET-1"
                     :collector-numbers ["1", "2", "3"]}
   "card-2" #:cardex{:code "SET-2"
                     :collector-numbers ["4"]}}

  #:card-list{:name "deck-1"
              :description "description-1"
              :cards [{:count 4, :name "card-1"}
                      {:count 4, :name "card-2"}]})
 => ()

 (list-missing-cards
  {}
  #:card-list{:name "deck-1"
              :description "description-1"
              :cards [{:count 4, :name "card-1"}
                      {:count 4, :name "card-2"}]})
 => ["card-1" "card-2"])


(facts
 "card-list->deck"

 (card-list->deck

  {"SET-1" {"1" #:card{:name "card-1"}
            "2" #:card{:name "card-1"}
            "3" #:card{:name "card-1"}}
   "SET-2" {"4" #:card{:name "card-2"}}}

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
           :decklines [{:deckline/card #:card{:name "card-1"}
                        :deckline/count 2}
                       {:deckline/card #:card{:name "card-1"}
                        :deckline/count 1}
                       {:deckline/card #:card{:name "card-1"}
                        :deckline/count 1}
                       {:deckline/card #:card{:name "card-2"}
                        :deckline/count 4}]}

 (card-list->deck
  {}
  {}
  #:card-list{:name "deck-1"
              :description "description-1"
              :cards [{:count 4, :name "card-1"}
                      {:count 4, :name "card-2"}]})
 => (throws AssertionError))


(facts
 "highres deck?"

 (highres-deck? #:deck{:decklines [{:deckline/card #:card{:highres? true}}
                                   {:deckline/card #:card{:highres? true}}]})
 => true

 (highres-deck? #:deck{:decklines [{:deckline/card #:card{:highres? true}}
                                   {:deckline/card #:card{:highres? false}}]})
 => false)


(facts
 "deck -> editions"

 (deck->editions #:deck{:decklines [{:deckline/card #:card{:code "set-1"}}
                                    {:deckline/card #:card{:code "set-1"}}
                                    {:deckline/card #:card{:code "set-2"}}]})
 => #{"set-1" "set-2"})


(facts
 "deck -> count"
 (deck->count #:deck{:decklines [{:deckline/count 1}
                                 {:deckline/count 3}]})
 => 4)
