(ns gendeck
  (:require [decker.edition :as de]
            [decker.codex :as dx]
            [decker.core :as dc]
            [decker.tts :as dt]))


(def EDDEX (de/!read-eddex))
(def EDITION-CARDS (de/!read-edition-cards))


;; (let [edition "RQS"
;;       cardex (dx/gen-cardex EDITION-CARDS
;;                             :newest edition
;;                             :oldest edition)]
;;   (doseq [card-list (dc/!read-card-list edition)]
;;     (->> (dc/card-list->deck cardex card-list)
;;          (dt/deck->ttsdeck EDDEX)
;;          (dt/write-ttsdeck!))))

;; (let [edition "MIR"
;;       cardex (dx/gen-cardex EDITION-CARDS
;;                             :newest edition
;;                             :oldest edition)]
;;   (doseq [card-list (dc/!read-card-list edition)]
;;     (->> (dc/card-list->deck cardex card-list)
;;          (dt/deck->ttsdeck EDDEX)
;;          (dt/write-ttsdeck!))))

;; (let [edition "ITP"
;;       cardex (dx/gen-cardex EDITION-CARDS
;;                             :newest edition
;;                             :oldest edition)]
;;   (doseq [card-list (dc/!read-card-list edition)]
;;     (->> (dc/card-list->deck cardex card-list)
;;          (dt/deck->ttsdeck EDDEX)
;;          (dt/write-ttsdeck!))))

;; (let [edition "VIS"
;;       cardex (dx/gen-cardex EDITION-CARDS
;;                             :newest edition
;;                             :ignore #{"ITP" "MGB"}
;;                             :oldest "MIR" )]
;;   (doseq [card-list (dc/!read-card-list edition)]
;;     (->> (dc/card-list->deck cardex card-list)
;;          (dt/deck->ttsdeck EDDEX)
;;          (dt/write-ttsdeck!))))

;; (let [edition "5ED"
;;       cardex (dx/gen-cardex EDITION-CARDS
;;                             :newest edition
;;                             :oldest edition)]
;;   (doseq [card-list (dc/!read-card-list edition)]
;;     (->> (dc/card-list->deck cardex card-list)
;;          (dt/deck->ttsdeck EDDEX)
;;          (dt/write-ttsdeck!))))

;; (let [edition "POR"
;;       cardex (dx/gen-cardex EDITION-CARDS
;;                             :newest edition
;;                             :oldest edition)]
;;   (doseq [card-list (dc/!read-card-list edition)]
;;     (->> (dc/card-list->deck cardex card-list)
;;          (dt/deck->ttsdeck EDDEX)
;;          (dt/write-ttsdeck!))))

(let [edition "WTH"
      cardex (dx/gen-cardex EDITION-CARDS
                            :newest edition
                            :ignore #{"POR" "PPOD" "PVAN" "PAST" "PMIC" "ITP" "MGB"}
                            :oldest "MIR")]
  (doseq [card-list (dc/!read-card-list edition)]
    (->> (dc/card-list->deck cardex card-list)
         (dt/deck->ttsdeck EDDEX)
         (dt/write-ttsdeck!))))
