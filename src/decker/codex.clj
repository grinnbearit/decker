(ns decker.codex
  (:require [decker.edition :as de]))


;; https://stackoverflow.com/questions/30921066/clojure-take-while-to-include-last-item-when-predicate-is-false
(defn take-while-and-one
  [pred coll]
  (lazy-seq
   (when-let [s (seq coll)]
     (if (pred (first s))
       (cons (first s) (take-while-and-one pred (rest s)))
       (list (first s))))))


(defn filter-editions
  "Given an edition-list returns a sublist of editions from `newest` to `oldest` ignores `ignore`"
  [edition-list & {:keys [newest oldest ignore]}]
  (let [ignore-set (set ignore)]
    (->> edition-list
         (drop-while #(and newest (not= (:edition/code %) newest)))
         (remove #(-> % :edition/code ignore-set))
         (take-while-and-one #(not (and oldest (= (:edition/code %) oldest)))))))


(defn !read-cardex
  [& {:keys [newest oldest ignore] :as opts}]
  (letfn [(reducer [acc [code {card-name :card/name collector-number :card/collector-number}]]
            (update-in acc [card-name] (fnil conj [])
                       {:edition/code code
                        :card/collector-number collector-number}))]

    (->> (for [{code :edition/code} (filter-editions (de/!read-edition-list) opts)
               card (de/!read-edition code)]
           [code card])
         (reduce reducer {}))))
