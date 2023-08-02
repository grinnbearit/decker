(ns decker.layout
  (:require [clojure.data.csv :as csv]
            [clojure.java.io :as io]
            [sanitize-filename.core :as sf]))


(defn deck->laylines
  "returns a list of dicts with a png url and a count,
  double-faced cards add 1 line for each face"
  [deck]
  (flatten
   (for [deckline (:deck/decklines deck)
         :let [card (:deckline/card deckline)]]
     (case (:card/layout-category card)
       (:normal :split)
       {:png (:card/png card) :count (:deckline/count deckline)}

       :transform
       (for [face (:card/faces card)]
         {:png (:png face) :count (:deckline/count deckline)})))))


(defn write-layout!
  [deck]
  (let [filename (format "%s.csv" (sf/sanitize (:deck/name deck)))]
    (with-open [writer (io/writer filename)]
      (csv/write-csv writer [["png" "count"]])
      (csv/write-csv writer (map (juxt :png :count) (deck->laylines deck))))))
