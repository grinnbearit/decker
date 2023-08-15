(ns gendeck
  (:require [decker.edition :as de]
            [decker.codex :as dx]
            [decker.core :as dc]
            [decker.tts :as dt]
            [decker.layout :as dl]
            [clojure.set :as set]))


(defonce EDITION-CARDS (de/!read-edition-cards))
(defonce EDDEX (de/!read-eddex))


(defn !test-decks
  "Returns a status map for all decks in the passed edition
  {:name :missing :highres? :editions}

  :highres? and :editions are only non nil if no cards are missing"
  [edition-cards eddex edition & {:keys [newest oldest ignore include]}]
  (let [cardex (dx/gen-cardex edition-cards
                              :newest (or newest edition)
                              :oldest (or oldest edition)
                              :ignore (-> (de/peripheral-editions EDDEX)
                                          (set/union ignore)
                                          (set/difference include)
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
  [edition-cards eddex edition & {:keys [newest oldest ignore include]}]
  (let [cardex (dx/gen-cardex edition-cards
                              :newest (or newest edition)
                              :oldest (or oldest edition)
                              :ignore (-> (de/peripheral-editions EDDEX)
                                          (set/union ignore)
                                          (set/difference include)
                                          (disj edition)))]
    (doseq [card-list (dc/!read-card-lists edition)]
      (->> (dc/card-list->deck eddex cardex card-list)
           (dt/deck->tts-deck)
           (dt/write-tts-deck!)))))


(defn write-layouts!
  "writes all decks in the layout format in the passed edition, assumes no issues"
  [edition-cards eddex edition & {:keys [newest oldest ignore include]}]
  (let [cardex (dx/gen-cardex edition-cards
                              :newest (or newest edition)
                              :oldest (or oldest edition)
                              :ignore (-> (de/peripheral-editions EDDEX)
                                          (set/union ignore)
                                          (set/difference include)
                                          (disj edition)))]
    (doseq [card-list (dc/!read-card-lists edition)]
      (->> (dc/card-list->deck eddex cardex card-list)
           (dl/write-layout!)))))


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
  (write-decks! EDITION-CARDS EDDEX "JUD" :oldest "ODY")
  (write-decks! EDITION-CARDS EDDEX "WC02")
  (write-decks! EDITION-CARDS EDDEX "ONS")
  (write-decks! EDITION-CARDS EDDEX "LGN" :oldest "ONS")
  (write-decks! EDITION-CARDS EDDEX "SCG" :oldest "ONS")
  (write-decks! EDITION-CARDS EDDEX "8ED")
  (write-decks! EDITION-CARDS EDDEX "WC03")
  (write-decks! EDITION-CARDS EDDEX "MRD")
  (write-decks! EDITION-CARDS EDDEX "DST" :oldest "MRD")
  (write-decks! EDITION-CARDS EDDEX "5DN" :oldest "MRD")
  (write-decks! EDITION-CARDS EDDEX "WC04")
  (write-decks! EDITION-CARDS EDDEX "CHK")
  (write-decks! EDITION-CARDS EDDEX "BOK" :oldest "CHK")
  (write-decks! EDITION-CARDS EDDEX "SOK" :oldest "CHK")
  (write-decks! EDITION-CARDS EDDEX "9ED")
  (write-decks! EDITION-CARDS EDDEX "RAV")
  (write-decks! EDITION-CARDS EDDEX "GPT" :oldest "RAV")
  (write-decks! EDITION-CARDS EDDEX "DIS" :oldest "RAV")
  (write-decks! EDITION-CARDS EDDEX "CSP" :oldest "ICE"
                :ignore #{"5ED" "MMQ" "MIR" "9ED" "INV" "6ED" "RAV" "CHK"
                          "MRD" "8ED" "ONS" "ODY" "7ED" "TMP" "USG"})
  (write-decks! EDITION-CARDS EDDEX "TSP" :oldest "TSB" :include #{"TSB"})
  (write-decks! EDITION-CARDS EDDEX "PLC" :oldest "TSB" :include #{"PLB" "TSB"})
  (write-decks! EDITION-CARDS EDDEX "FUT" :oldest "TSB" :include #{"PLB" "TSB"})
  (write-decks! EDITION-CARDS EDDEX "10E")
  (write-decks! EDITION-CARDS EDDEX "PSAL" :newest "10E" :oldest "INV")
  (write-decks! EDITION-CARDS EDDEX "LRW")
  (write-decks! EDITION-CARDS EDDEX "EVG")
  (write-decks! EDITION-CARDS EDDEX "MOR" :oldest "LRW")
  (write-decks! EDITION-CARDS EDDEX "SHM" :oldest "10E")
  (write-decks! EDITION-CARDS EDDEX "EVE" :oldest "SHM")
  (write-decks! EDITION-CARDS EDDEX "ME2" :oldest "ME1" :include #{"ME1"} :ignore #{"SHM" "LRW"})
  (write-decks! EDITION-CARDS EDDEX "ALA" :oldest "10E")
  (write-decks! EDITION-CARDS EDDEX "DD2")
  (write-decks! EDITION-CARDS EDDEX "CON" :oldest "10E")
  (write-decks! EDITION-CARDS EDDEX "DDC")
  (write-decks! EDITION-CARDS EDDEX "ARB" :oldest "10E")
  (write-decks! EDITION-CARDS EDDEX "M10")
  (write-decks! EDITION-CARDS EDDEX "HOP" :oldest "OHOP" :include #{"OHOP"})
  (write-decks! EDITION-CARDS EDDEX "ZEN" :oldest "M10")
  (write-decks! EDITION-CARDS EDDEX "DDD")
  (write-decks! EDITION-CARDS EDDEX "WWK" :oldest "M10")
  (write-decks! EDITION-CARDS EDDEX "DDE")
  (write-decks! EDITION-CARDS EDDEX "ROE" :oldest "M10")
  (write-decks! EDITION-CARDS EDDEX "DPA")
  (write-decks! EDITION-CARDS EDDEX "ARC" :oldest "OARC" :include #{"OARC"})
  (write-decks! EDITION-CARDS EDDEX "M11" :oldest "ZEN")
  (write-decks! EDITION-CARDS EDDEX "DDF")
  (write-decks! EDITION-CARDS EDDEX "SOM" :oldest "M11")
  (write-decks! EDITION-CARDS EDDEX "TD0")
  (write-decks! EDITION-CARDS EDDEX "MBS" :oldest "ZEN")
  (write-decks! EDITION-CARDS EDDEX "DDG")
  (write-decks! EDITION-CARDS EDDEX "NPH" :oldest "ZEN")
  (write-decks! EDITION-CARDS EDDEX "CMD")
  (write-decks! EDITION-CARDS EDDEX "M12" :oldest "ZEN")
  (write-decks! EDITION-CARDS EDDEX "DDH")
  (write-decks! EDITION-CARDS EDDEX "ISD" :oldest "SOM")
  (write-decks! EDITION-CARDS EDDEX "DKA" :oldest "SOM")
  (write-decks! EDITION-CARDS EDDEX "DDI")
  (write-decks! EDITION-CARDS EDDEX "AVR" :oldest "SOM")
  (write-decks! EDITION-CARDS EDDEX "PC2" :oldest "OPC2" :include #{"OPC2"})
  (write-decks! EDITION-CARDS EDDEX "M13" :oldest "SOM")
  (write-decks! EDITION-CARDS EDDEX "DDJ")
  (write-decks! EDITION-CARDS EDDEX "RTR" :oldest "ISD")
  (write-decks! EDITION-CARDS EDDEX "GTC" :oldest "ISD")
  (write-decks! EDITION-CARDS EDDEX "DDK")
  (write-decks! EDITION-CARDS EDDEX "DGM" :oldest "M13")
  (write-decks! EDITION-CARDS EDDEX "M14" :oldest "5ED")
  (write-decks! EDITION-CARDS EDDEX "DDL")
  (write-decks! EDITION-CARDS EDDEX "THS" :oldest "M14")
  (write-decks! EDITION-CARDS EDDEX "C13")
  (write-decks! EDITION-CARDS EDDEX "BNG" :oldest "M14")
  (write-decks! EDITION-CARDS EDDEX "DDM")
  (write-decks! EDITION-CARDS EDDEX "JOU" :oldest "M14")
  (write-decks! EDITION-CARDS EDDEX "M15" :oldest "THS")
  (write-decks! EDITION-CARDS EDDEX "DDN")
  (write-decks! EDITION-CARDS EDDEX "KTK" :oldest "M15")
  (write-decks! EDITION-CARDS EDDEX "C14")
  (write-decks! EDITION-CARDS EDDEX "FRF" :oldest "THS")
  (write-decks! EDITION-CARDS EDDEX "DDO")
  (write-decks! EDITION-CARDS EDDEX "DTK")
  (write-decks! EDITION-CARDS EDDEX "ORI" :oldest "KTK")
  (write-decks! EDITION-CARDS EDDEX "DDP")
  (write-decks! EDITION-CARDS EDDEX "BFZ")
  (write-decks! EDITION-CARDS EDDEX "C15")
  (write-decks! EDITION-CARDS EDDEX "OGW" :oldest "BFZ")
  (write-decks! EDITION-CARDS EDDEX "DDQ")
  (write-decks! EDITION-CARDS EDDEX "SOI")
  (write-decks! EDITION-CARDS EDDEX "W16" :oldest "BFZ")
  (write-decks! EDITION-CARDS EDDEX "EMN" :oldest "SOI")
  (write-decks! EDITION-CARDS EDDEX "DDR")
  (write-decks! EDITION-CARDS EDDEX "KLD")
  (write-decks! EDITION-CARDS EDDEX "C16")
  (write-decks! EDITION-CARDS EDDEX "AER" :oldest "KLD")
  (write-decks! EDITION-CARDS EDDEX "DDS")
  (write-decks! EDITION-CARDS EDDEX "AKH")
  (write-decks! EDITION-CARDS EDDEX "W17" :oldest "KLD")
  (write-decks! EDITION-CARDS EDDEX "CMA")
  (write-decks! EDITION-CARDS EDDEX "E01" :oldest "AKH" :include #{"OE01"})
  (write-decks! EDITION-CARDS EDDEX "HOU" :oldest "AKH")
  (write-decks! EDITION-CARDS EDDEX "C17")
  (write-decks! EDITION-CARDS EDDEX "XLN")
  (write-decks! EDITION-CARDS EDDEX "DDT")
  (write-decks! EDITION-CARDS EDDEX "E02" :oldest "XLN")
  (write-decks! EDITION-CARDS EDDEX "RIX" :oldest "XLN")
  (write-decks! EDITION-CARDS EDDEX "DDU")
  (write-decks! EDITION-CARDS EDDEX "challenger" :newest "RIX" :oldest "KLD")
  (write-decks! EDITION-CARDS EDDEX "DOM")
  (write-decks! EDITION-CARDS EDDEX "CM2")
  (write-decks! EDITION-CARDS EDDEX "GS1")
  (write-decks! EDITION-CARDS EDDEX "M19")
  (write-decks! EDITION-CARDS EDDEX "C18")
  (write-decks! EDITION-CARDS EDDEX "GRN")
  (write-decks! EDITION-CARDS EDDEX "GK1" :oldest "GRN" :include #{"GK1"})
  (write-decks! EDITION-CARDS EDDEX "GNT" :newest "GNT" :oldest "M19" :include #{"GNT"})
  (write-decks! EDITION-CARDS EDDEX "SK1" :newest "GNT" :oldest "XLN" :include #{"GK1" "GNT"})
  (write-decks! EDITION-CARDS EDDEX "RNA")
  (write-decks! EDITION-CARDS EDDEX "GK2" :newest "GK2" :oldest "RNA" :include #{"GK2"})
  (write-decks! EDITION-CARDS EDDEX "Q02" :newest "GK2" :oldest "XLN")
  (write-decks! EDITION-CARDS EDDEX "WAR")
  (write-decks! EDITION-CARDS EDDEX "M20" :oldest "GRN")
  (write-decks! EDITION-CARDS EDDEX "C19")
  (write-decks! EDITION-CARDS EDDEX "ELD" :oldest "GRN")
  (write-decks! EDITION-CARDS EDDEX "Q03" :newest "ELD" :oldest "GNR")

  ;; time skip
  (write-decks! EDITION-CARDS EDDEX "AFR" :oldest "AFC" :include #{"AFC"})
  (write-decks! EDITION-CARDS EDDEX "TAFR" :oldest "TAFR" :include #{"TAFR"})
  (write-decks! EDITION-CARDS EDDEX "2021_arena_starter_kit" :newest "AFR" :oldest "ZNR")
  (write-decks! EDITION-CARDS EDDEX "MID" :oldest "MIC" :include #{"MIC"})
  (write-decks! EDITION-CARDS EDDEX "Q06" :oldest "GTC")
  (write-decks! EDITION-CARDS EDDEX "VOW" :oldest "MID" :include #{"VOC"})
  (write-decks! EDITION-CARDS EDDEX "NEO" :oldest "NEC" :include #{"NEC"})
  (write-decks! EDITION-CARDS EDDEX "Q07" :oldest "ZNR")
  (write-decks! EDITION-CARDS EDDEX "SNC" :oldest "NCC" :include #{"NCC"})
  (write-decks! EDITION-CARDS EDDEX "2022_starter_kit" :newest "SNC" :oldest "MID")
  (write-decks! EDITION-CARDS EDDEX "CLB")
  (write-decks! EDITION-CARDS EDDEX "DMU" :oldest "DMC" :include #{"DMC"})
  (write-decks! EDITION-CARDS EDDEX "40K")
  (write-decks! EDITION-CARDS EDDEX "GN3")
  (write-decks! EDITION-CARDS EDDEX "Q08" :newest "GN3" :oldest "RTR")
  (write-decks! EDITION-CARDS EDDEX "BRO" :oldest "BRC" :include #{"BRC"})
  (write-decks! EDITION-CARDS EDDEX "J22")
  (write-decks! EDITION-CARDS EDDEX "SCD")
  (write-decks! EDITION-CARDS EDDEX "ONE" :oldest "ONC" :include #{"ONC"}))
