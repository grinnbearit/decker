(ns gendeck
  (:require [decker.edition :as de]
            [decker.codex :as dx]
            [decker.core :as dc]
            [decker.tts :as dt]))


(defonce EDITION-CARDS (de/!read-edition-cards))
(defonce EDDEX (de/!read-eddex))


(defn !test-decks
  "Returns a status map for all decks in the passed edition
  {:name :missing :highres? :editions}

  :highres? and :editions are only non nil if no cards are missing"
  [edition-cards eddex edition & {:keys [oldest]}]
  (let [cardex (dx/gen-cardex edition-cards
                              :newest edition
                              :oldest (or oldest edition)
                              :ignore (disj (de/peripheral-editions eddex)
                                            edition))]
    (for [card-list (dc/!read-card-lists edition)
          :let [missing-cards (dc/list-missing-cards cardex card-list)]]
      (if (seq missing-cards)
        {:name (:card-list/name card-list)
         :missing missing-cards}
        (let [deck (dc/card-list->deck eddex cardex card-list)]
          {:name (:card-list/name card-list)
           :highres? (dc/highres-deck? deck)
           :editions (dc/deck->editions deck)})))))


(defn write-decks!
  "writes all decks in the passed edition, assumes no issues"
  [edition-cards eddex edition & {:keys [oldest]}]
  (let [cardex (dx/gen-cardex edition-cards
                              :newest edition
                              :oldest (or oldest edition)
                              :ignore (disj (de/peripheral-editions EDDEX)
                                            edition))]
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
  ;; time skip
  (write-decks! EDITION-CARDS EDDEX "GTC" :oldest "ISD")
  (write-decks! EDITION-CARDS EDDEX "DDK")
  (write-decks! EDITION-CARDS EDDEX "DGM" :oldest "M13")
  (write-decks! EDITION-CARDS EDDEX "M14" :oldest "5ED")
  (write-decks! EDITION-CARDS EDDEX "DDL")
  (write-decks! EDITION-CARDS EDDEX "THS" :oldest "M14"))
