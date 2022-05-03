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


(defn filter-edition-cards
  "Given an edition-cards list returns a sublist of editions from `newest` to `oldest` ignores `ignore`"
  [edition-cards & {:keys [newest oldest ignore]}]
  (let [ignore-set (set ignore)]
    (->> edition-cards
         (drop-while #(and newest (not= (:edition-cards/code %) newest)))
         (remove #(-> % :edition-cards/code ignore-set))
         (take-while-and-one #(not (and oldest (= (:edition-cards/code %) oldest)))))))


(defn gen-cardex
  "Returns a mapping of card/name -> {cardex/code code :cardex/collector-numbers []}
  for the most recent edition"
  [edition-cards & {:keys [newest oldest ignore] :as opts}]
  (letfn [(reducer [acc [code {card-name :card/name collector-number :card/collector-number}]]
            (cond (and (contains? acc card-name)
                       (= (get-in acc [card-name :cardex/code]) code))
                  (update-in acc [card-name :cardex/collector-numbers] conj collector-number)

                  (contains? acc card-name)
                  acc

                  :else
                  (assoc acc card-name #:cardex{:code code :collector-numbers [collector-number]})))]

    (->> (for [{code :edition-cards/code cards :edition-cards/cards} (filter-edition-cards edition-cards opts)
               card cards]
           [code card])
         (reduce reducer {}))))
