(ns decker.codex-test
  (:use midje.sweet
        decker.codex)
  (:require [decker.edition :as de]))


(facts
 "take while and one"
 (take-while odd? [1 3 5 7 2 4 6]) => [1 3 5 7]
 (take-while-and-one odd? [1 3 5 7 2 4 6]) => [1 3 5 7 2])


(facts
 "filter edition-cards"
 (let [edition-cards [#:edition-cards{:code "SET-4", :cards []}
                      #:edition-cards{:code "SET-3", :cards []}
                      #:edition-cards{:code "SET-2", :cards []}
                      #:edition-cards{:code "SET-1", :cards []}]]

   (filter-edition-cards edition-cards) => edition-cards
   (filter-edition-cards edition-cards :newest "SET-3") => (drop 1 edition-cards)
   (filter-edition-cards edition-cards :oldest "SET-2") => (take 3 edition-cards)
   (filter-edition-cards edition-cards :ignore ["SET-3", "SET-2"]) => (concat (take 1 edition-cards) (drop 3 edition-cards))))


(facts
 "gen-cardex"

 (let [edition-cards [#:edition-cards{:code "SET-2"
                                      :cards [#:card{:collector-number "3"
                                                     :name "card-1"}
                                              #:card{:collector-number "4"
                                                     :name "card-1"}]}

                      #:edition-cards{:code "SET-1"
                                      :cards [#:card{:collector-number "1"
                                                     :name "card-1"}
                                              #:card{:collector-number "2"
                                                     :name "card-2"}]}]]

   (gen-cardex edition-cards :oldest "SET-2")
   => {"card-1" #:cardex{:code "SET-2"
                         :collector-numbers ["3" "4"]}}

   (provided
    (filter-edition-cards edition-cards {:oldest "SET-2"})
    => (take 1 edition-cards))


   (gen-cardex edition-cards)
   => {"card-1" #:cardex{:code "SET-2"
                         :collector-numbers ["3" "4"]}
       "card-2" #:cardex{:code "SET-1"
                         :collector-numbers ["2"]}}))
