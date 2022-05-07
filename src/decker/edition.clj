(ns decker.edition
  (:require [clj-http.client :as client]
            [clojure.pprint :as pprint]
            [net.cgrand.enlive-html :as html]
            [clojure.string :as str]
            [clojure.instant :as inst]
            [clojure.java.io :as io]
            [clojure.edn :as edn]))


(defn !fetch-edition-list
  "returns a list of editions found at https://scryfall.com/sets"
  []
  (let [content (html/html-resource (java.net.URL. "https://scryfall.com/sets"))]
    (for [row (html/select content [:table.checklist :> :tbody :tr])
          :when (= (first (html/select row [:a.pillbox-item html/text])) "en")
          :let [[edition-name _ edition-code _ cardinality date] (->> (drop 1 (html/select row [:td :a html/text]))
                                                                      (drop-while map?))]]
      #:edition{:date (inst/read-instant-date date)
                :code edition-code
                :name (str/trim edition-name)})))


(defn write-edition-list!
  "Writes a list of editions to metadata/editions.edn"
  [edition-list]
  (with-open [f (io/writer "metadata/editions.edn")]
    (binding [*out* f]
      (pprint/pprint edition-list))))


(defn !read-edition-list
  "Reads the current list of editions from metadata/editions.edn

  If the file doesn't exist, returns ()"
  []
  (with-open [f (io/reader "metadata/editions.edn")]
    (edn/read (java.io.PushbackReader. f))))


(defn !fetch-edition
  "Given the 3 letter code for a edition, returns a list of card metadata from scryfall"
  [edition]
  (letfn [(->card [scryfall-card]
            #:card{:collector-number (:collector_number scryfall-card)
                   :name (get scryfall-card :name)
                   :png (get-in scryfall-card [:image_uris :png])
                   :type-line (get scryfall-card :type_line)
                   :oracle-text (get scryfall-card :oracle_text)
                   :layout (get scryfall-card :layout)
                   :highres? (get scryfall-card :highres_image)})]

    (loop [acc [] page 1 has-more? true]
      (if (not has-more?)
        (->> (apply concat acc)
             (map ->card))
        (let [response (client/get "https://api.scryfall.com/cards/search"
                                   {:query-params {"order" "set"
                                                   "q" (format "e:%s unique:prints" edition)
                                                   "page" page}
                                    :as :json})]
          (Thread/sleep 50)
          (recur (conj acc (get-in response [:body :data]))
                 (inc page)
                 (get-in response [:body :has_more])))))))


(defn write-edition!
  "writes edition metadata to a file named metadata/{edition}_metadata.edn"
  [edition card-list]
  (let [filename (format "metadata/%s_metadata.edn" edition)]
    (with-open [f (io/writer filename)]
      (binding [*out* f]
        (pprint/pprint card-list)))))


(defn !read-edition
  "returns a list of card metadata for the passed edition"
  [edition]
  (let [filename (format "metadata/%s_metadata.edn" edition)]
    (with-open [f (io/reader filename)]
      (edn/read (java.io.PushbackReader. f)))))


(defn !read-edition-cards
  "returns a list of  cards for all editions, in order from newest to oldest"
  []
  (for [{code :edition/code} (!read-edition-list)]
    #:edition-cards{:code code
                    :cards (!read-edition code)}))


(defn !read-eddex
  "returns a map of edition -> collector-number -> card"
  []
  (letfn [(reducer [acc [code card]]
            (assoc-in acc [code (:card/collector-number card)] card))]

    (->> (for [{code :edition/code} (!read-edition-list)
               card (!read-edition code)]
           [code card])
         (reduce reducer {}))))
