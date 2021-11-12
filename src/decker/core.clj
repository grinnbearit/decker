(ns decker.core
  (:require [net.cgrand.enlive-html :as html]
            [clojure.string :as str]
            [clojure.instant :as inst]
            [clojure.java.io :as io]
            [clojure.edn :as edn]))


(defn fetch-all-sets
  "returns a list of sets found at https://scryfall.com/sets"
  []
  (let [content (html/html-resource (java.net.URL. "https://scryfall.com/sets"))]
    (for [row (html/select content [:table.checklist :> :tbody :tr])
          :when (= (first (html/select row [:a.pillbox-item html/text])) "en")
          :let [[set-name _ set-code _ cardinality date] (->> (drop 1 (html/select row [:td :a html/text]))
                                                              (drop-while map?))]]
      #:all-sets{:set-name (str/trim set-name)
                 :set-code set-code
                 :cardinality (Integer/parseInt cardinality)
                 :date (inst/read-instant-date date)})))


(defn write-all-sets!
  "Writes a list of all-sets to all_sets.edn"
  [all-sets]
  (with-open [f (io/writer "all_sets.edn")]
    (binding [*out* f]
      (pr all-sets))))


(defn read-all-sets
  "Reads the current list of all-sets from all_sets.edn

  If the file doesn't exist, returns ()"
  []
  (with-open [f (io/reader "all_sets.edn")]
    (edn/read (java.io.PushbackReader. f))))
