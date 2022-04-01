(ns decker.core
  (:require [clj-http.client :as client]
            [net.cgrand.enlive-html :as html]
            [clojure.string :as str]
            [clojure.instant :as inst]
            [clojure.java.io :as io]
            [clojure.edn :as edn]))


(defn fetch-edition-list
  "returns a list of sets found at https://scryfall.com/sets"
  []
  (let [content (html/html-resource (java.net.URL. "https://scryfall.com/sets"))]
    (for [row (html/select content [:table.checklist :> :tbody :tr])
          :when (= (first (html/select row [:a.pillbox-item html/text])) "en")
          :let [[edition-name _ edition-code _ cardinality date] (->> (drop 1 (html/select row [:td :a html/text]))
                                                                      (drop-while map?))]]
      #:edition-list{:edition-name (str/trim edition-name)
                     :edition-code edition-code
                     :cardinality (Integer/parseInt cardinality)
                     :date (inst/read-instant-date date)})))


(defn write-edition-list!
  "Writes a list of all-sets to metadata/edition_list.edn"
  [edition-list]
  (with-open [f (io/writer "metadata/edition_list.edn")]
    (binding [*out* f]
      (pr edition-list))))


(defn read-edition-list
  "Reads the current list of all-sets from metadata/edition_list.edn

  If the file doesn't exist, returns ()"
  []
  (with-open [f (io/reader "metadata/edition_list.edn")]
    (edn/read (java.io.PushbackReader. f))))


(defn fetch-edition
  "Given the 3 letter code for a edition, returns a list of card metadata from scryfall"
  [edition]
  (loop [acc [] page 1 has-more? true]
    (if (not has-more?)
      (apply concat acc)
      (let [response (client/get "https://api.scryfall.com/cards/search"
                                 {:query-params {"order" "set"
                                                 "q" (format "e:%s unique:prints" "lea")
                                                 "page" page}
                                  :as :json})]
        (Thread/sleep 50)
        (recur (conj acc (get-in response [:body :data]))
               (inc page)
               (get-in response [:body :has_more]))))))


(defn write-edition!
  "writes edition metadata to a file named metadata/{edition}_metadata.edn
  assumes all cards are from the same edition"
  [edition-metadata]
  (let [edition (:set (first edition-metadata))
        filename (format "metadata/%s_metadata.edn" edition)]
    (with-open [f (io/writer filename)]
      (binding [*out* f]
        (pr edition-metadata)))))


(defn read-edition
  "returns a list of card metadata for the passed edition"
  [edition]
  (let [filename (format "metadata/%s_metadata.edn" edition)]
    (with-open [f (io/reader filename)]
      (edn/read (java.io.PushbackReader. f)))))
