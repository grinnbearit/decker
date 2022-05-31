(ns gendeck
  (:require [decker.edition :as de]
            [decker.codex :as dx]
            [decker.core :as dc]
            [decker.tts :as dt]
            [clojure.set :as set]))


(defonce EDITION-CARDS (de/!read-edition-cards))
(defonce EDDEX (de/!read-eddex))


(defn !test-decks
  "Returns a status map for all decks in the passed edition
  {:name :missing :highres? :editions}

  :highres? and :editions are only non nil if no cards are missing"
  [edition-cards eddex edition & {:keys [oldest ignore]}]
  (let [cardex (dx/gen-cardex edition-cards
                              :newest edition
                              :oldest (or oldest edition)
                              :ignore (-> (de/peripheral-editions EDDEX)
                                          (set/union ignore)
                                          (disj edition)))]
    (for [card-list (dc/!read-card-lists edition)
          :let [missing-cards (dc/list-missing-cards cardex card-list)]]
      (if (seq missing-cards)
        {:name (:card-list/name card-list)
         :missing missing-cards}
        (let [deck (dc/card-list->deck eddex cardex card-list)]
          {:name (:card-list/name card-list)
           :highres? (dc/highres-deck? deck)
           :editions (dc/deck->editions deck)
           :count (dc/deck->count deck)})))))


(defn write-decks!
  "writes all decks in the passed edition, assumes no issues"
  [edition-cards eddex edition & {:keys [oldest ignore]}]
  (let [cardex (dx/gen-cardex edition-cards
                              :newest edition
                              :oldest (or oldest edition)
                              :ignore (-> (de/peripheral-editions EDDEX)
                                          (set/union ignore)
                                          (disj edition)))]
    (doseq [card-list (dc/!read-card-lists edition)]
      (->> (dc/card-list->deck eddex cardex card-list)
           (dt/deck->tts-deck)
           (dt/write-tts-deck!)))))


(comment
  (write-decks! EDITION-CARDS EDDEX "RQS")
  (write-decks! EDITION-CARDS EDDEX "MIR")
  (write-decks! EDITION-CARDS EDDEX "ITP")
  (write-decks! EDITION-CARDS EDDEX "VIS" :oldest "MIR")
  (write-decks! EDITION-CARDS EDDEX "5ED")
  (write-decks! EDITION-CARDS EDDEX "POR")
  (write-decks! EDITION-CARDS EDDEX "WTH" :oldest "MIR")
  (write-decks! EDITION-CARDS EDDEX "WC97")
  (write-decks! EDITION-CARDS EDDEX "TMP")
  (write-decks! EDITION-CARDS EDDEX "STH" :oldest "TMP")
  (write-decks! EDITION-CARDS EDDEX "EXO" :oldest "TMP")
  (write-decks! EDITION-CARDS EDDEX "P02")
  (write-decks! EDITION-CARDS EDDEX "WC98")
  (write-decks! EDITION-CARDS EDDEX "USG")
  (write-decks! EDITION-CARDS EDDEX "ATH")
  (write-decks! EDITION-CARDS EDDEX "ULG" :oldest "USG")
  (write-decks! EDITION-CARDS EDDEX "6ED")
  (write-decks! EDITION-CARDS EDDEX "UDS" :oldest "USG")
  (write-decks! EDITION-CARDS EDDEX "PTK")
  (write-decks! EDITION-CARDS EDDEX "WC99")
  (write-decks! EDITION-CARDS EDDEX "S99")
  (write-decks! EDITION-CARDS EDDEX "MMQ")
  (write-decks! EDITION-CARDS EDDEX "BRB")
  (write-decks! EDITION-CARDS EDDEX "NEM" :oldest "MMQ")
  (write-decks! EDITION-CARDS EDDEX "S00" :oldest "6ED" :ignore #{"MMQ"})
  (write-decks! EDITION-CARDS EDDEX "PCY" :oldest "MMQ")
  (write-decks! EDITION-CARDS EDDEX "WC00")
  (write-decks! EDITION-CARDS EDDEX "BTD")
  (write-decks! EDITION-CARDS EDDEX "INV")
  (write-decks! EDITION-CARDS EDDEX "PLS" :oldest "INV")
  (write-decks! EDITION-CARDS EDDEX "7ED")
  (write-decks! EDITION-CARDS EDDEX "APC" :oldest "INV" :ignore #{"7ED"})
  (write-decks! EDITION-CARDS EDDEX "WC01")
  (write-decks! EDITION-CARDS EDDEX "ODY")
  (write-decks! EDITION-CARDS EDDEX "DKM")
  (write-decks! EDITION-CARDS EDDEX "TOR" :oldest "ODY")
  ;; time skip
  (write-decks! EDITION-CARDS EDDEX "GTC" :oldest "ISD")
  (write-decks! EDITION-CARDS EDDEX "DDK")
  (write-decks! EDITION-CARDS EDDEX "DGM" :oldest "M13")
  (write-decks! EDITION-CARDS EDDEX "M14" :oldest "5ED")
  (write-decks! EDITION-CARDS EDDEX "DDL")
  (write-decks! EDITION-CARDS EDDEX "THS" :oldest "M14")
  (write-decks! EDITION-CARDS EDDEX "C13"))
