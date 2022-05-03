(ns gendeck
  (:require [decker.edition :as de]
            [decker.core :as dc]
            [decker.tts :as dt]))


(def EDDEX (de/!read-eddex))
(def EDITION-CARDS (de/!read-edition-cards))


;; (doseq [card-list (dc/!read-card-list "RQS")]
;;   (->> (dc/card-list->deck EDITION-CARDS card-list :newest "RQS" :oldest "RQS")
;;        (dt/deck->ttsdeck EDDEX)
;;        (dt/write-ttsdeck!)))

;; (doseq [card-list (dc/!read-card-list "MIR")]
;;   (->> (dc/card-list->deck EDITION-CARDS card-list :newest "MIR" :oldest "MIR")
;;        (dt/deck->ttsdeck EDDEX)
;;        (dt/write-ttsdeck!)))

(doseq [card-list (dc/!read-card-list "ITP")]
  (->> (dc/card-list->deck EDITION-CARDS card-list :newest "ITP" :oldest "ITP")
       (dt/deck->ttsdeck EDDEX)
       (dt/write-ttsdeck!)))
