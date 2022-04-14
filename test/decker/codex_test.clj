(ns decker.codex-test
  (:use midje.sweet
        decker.codex)
  (:require [decker.edition :as de]))


(facts
 "take while and one"
 (take-while odd? [1 3 5 7 2 4 6]) => [1 3 5 7]
 (take-while-and-one odd? [1 3 5 7 2 4 6]) => [1 3 5 7 2])


(facts
 "filter eddex"
 (let [eddex [#:eddex{:code "SET-4", :cards []}
              #:eddex{:code "SET-3", :cards []}
              #:eddex{:code "SET-2", :cards []}
              #:eddex{:code "SET-1", :cards []}]]

   (filter-eddex eddex) => eddex
   (filter-eddex eddex :newest "SET-3") => (drop 1 eddex)
   (filter-eddex eddex :oldest "SET-2") => (take 3 eddex)
   (filter-eddex eddex :ignore ["SET-3", "SET-2"]) => (concat (take 1 eddex) (drop 3 eddex))))


(facts
 "gen-cardex"

 (let [eddex [#:eddex{:code "SET-2"
                      :cards [#:card{:collector-number "3"
                                     :name "card-1"}]}

              #:eddex{:code "SET-1"
                      :cards [#:card{:collector-number "1"
                                     :name "card-1"}
                              #:card{:collector-number "2"
                                     :name "card-2"}]}]]

   (gen-cardex eddex :oldest "SET-2")
   => {"card-1" [{:edition/code "SET-2"
                  :card/collector-number "3"}]}

   (provided
    (filter-eddex eddex {:oldest "SET-2"})
    => (take 1 eddex))


   (gen-cardex eddex)
   => {"card-1" [{:edition/code "SET-2"
                  :card/collector-number "3"}
                 {:edition/code "SET-1"
                  :card/collector-number "1"}]
       "card-2" [{:edition/code "SET-1"
                  :card/collector-number "2"}]}))
