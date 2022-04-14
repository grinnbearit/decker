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


(defn filter-eddex
  "Given an edition-list returns a sublist of editions from `newest` to `oldest` ignores `ignore`"
  [eddex & {:keys [newest oldest ignore]}]
  (let [ignore-set (set ignore)]
    (->> eddex
         (drop-while #(and newest (not= (:eddex/code %) newest)))
         (remove #(-> % :eddex/code ignore-set))
         (take-while-and-one #(not (and oldest (= (:eddex/code %) oldest)))))))


(defn gen-cardex
  [eddex & {:keys [newest oldest ignore] :as opts}]
  (letfn [(reducer [acc [code {card-name :card/name collector-number :card/collector-number}]]
            (update-in acc [card-name] (fnil conj [])
                       {:edition/code code
                        :card/collector-number collector-number}))]

    (->> (for [{code :eddex/code cards :eddex/cards} (filter-eddex eddex opts)
               card cards]
           [code card])
         (reduce reducer {}))))
