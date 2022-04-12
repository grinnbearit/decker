(ns decker.codex-test
  (:use midje.sweet
        decker.codex)
  (:require [decker.edition :as de]))


(facts
 "take while and one"
 (take-while odd? [1 3 5 7 2 4 6]) => [1 3 5 7]
 (take-while-and-one odd? [1 3 5 7 2 4 6]) => [1 3 5 7 2])


(facts
 "filter editions"
 (let [edition-list [#:edition{:name "Unfinity",
                               :code "UNF",
                               :cardinality 26,
                               :date #inst "2022-12-31"}
                     #:edition{:name
                               "Commander Legends: Battle for Baldur's Gate",
                               :code "CLB",
                               :cardinality 27,
                               :date #inst "2022-06-10"}
                     #:edition{:name "Streets of New Capenna",
                               :code "SNC",
                               :cardinality 36,
                               :date #inst "2022-04-29"}
                     #:edition{:name "Wizards Play Network 2022",
                               :code "PW22",
                               :cardinality 4,
                               :date #inst "2022-03-05"}]]

   (filter-editions edition-list) => edition-list
   (filter-editions edition-list :newest "CLB") => (drop 1 edition-list)
   (filter-editions edition-list :oldest "SNC") => (take 3 edition-list)
   (filter-editions edition-list :ignore ["CLB"]) => (remove #(= "CLB" (:edition/code %)) edition-list)))


(facts
 "!read-cardex"
 (!read-cardex :newest "SET-2" :oldest "SET-1" :ignore #{"SET-3"})
 => {}

 (provided
  (filter-editions (de/!read-edition-list)
                   {:newest "SET-2"
                    :oldest "SET-1"
                    :ignore #{"SET-3"}})
  => [])


 (!read-cardex)
 => {"card-1" [{:card/collector-number "3"
                :edition/code "SET-2"}
               {:card/collector-number "1"
                :edition/code "SET-1"}]
     "card-2" [{:card/collector-number "2"
                :edition/code "SET-1"}]}

 (provided
  (filter-editions (de/!read-edition-list) nil)
  => [#:edition{:code "SET-2"}
      #:edition{:code "SET-1"}]

  (de/!read-edition "SET-2")
  => [#:card{:collector-number "3"
             :name "card-1"}]

  (de/!read-edition "SET-1")
  => [#:card{:collector-number "1"
             :name "card-1"}
      #:card{:collector-number "2"
             :name "card-2"}]))
