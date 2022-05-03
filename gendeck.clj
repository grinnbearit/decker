(ns gendeck
  (:require [decker.edition :as de]
            [decker.codex :as dx]
            [decker.core :as dc]
            [decker.tts :as dt]))


(def EDDEX (de/!read-eddex))
(def EDITION-CARDS (de/!read-edition-cards))


;; (let [cardex (dx/gen-cardex EDITION-CARDS :newst "RQS" :oldest "RQS")]
;;   (doseq [card-list (dc/!read-card-list "RQS")]
;;     (->> (dc/card-list->deck cardex card-list)
;;          (dt/deck->ttsdeck EDDEX)
;;          (dt/write-ttsdeck!))))

;; (let [cardex (dx/gen-cardex EDITION-CARDS :newst "MIR" :oldest "MIR")]
;;   (doseq [card-list (dc/!read-card-list "MIR")]
;;     (->> (dc/card-list->deck cardex card-list)
;;          (dt/deck->ttsdeck EDDEX)
;;          (dt/write-ttsdeck!))))

;; (let [cardex (dx/gen-cardex EDITION-CARDS :newst "ITP" :oldest "ITP")]
;;   (doseq [card-list (dc/!read-card-list "ITP")]
;;     (->> (dc/card-list->deck cardex card-list)
;;          (dt/deck->ttsdeck EDDEX)
;;          (dt/write-ttsdeck!))))

(let [cardex (dx/gen-cardex EDITION-CARDS :newst "VIS" :oldest "MIR" :ignore #{"ITP" "MGB"})]
  (doseq [card-list (dc/!read-card-list "VIS")]
    (->> (dc/card-list->deck cardex card-list)
         (dt/deck->ttsdeck EDDEX)
         (dt/write-ttsdeck!))))
