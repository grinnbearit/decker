(ns decker.tts
  (:require [clojure.java.io :as io]
            [cheshire.core :as json]
            [sanitize-filename.core :as sf]))


(def BACK-URL
  {"scheme" "http://cloud-3.steamusercontent.com/ugc/998016607072055936/0598975AB8EC26E8956D84F9EC73BBE5754E6C80/"
   "planar" "http://cloud-3.steamusercontent.com/ugc/998016607072060000/1713AE8643632456D06F1BBA962C5514DD8CCC76/"
   "normal" "http://cloud-3.steamusercontent.com/ugc/998016607072060763/7AFEF2CE9E7A7DB735C93CF33CC4C378CBF4B20D/"})


(defn card->ObjectState
  "returns an object state dict for a TTS deck,
  transformed? is used for double sided cards and returns an object for the reverse"
  ([card]
   (card->ObjectState card false))
  ([card transformed?]
   (case (:card/layout-category card)
     (:normal :split)
     {"FaceURL" (:card/png card)
      "BackURL" (get BACK-URL (:card/layout card) (BACK-URL "normal"))
      "NumHeight" 1
      "NumWidth" 1
      "BackIsHidden" true}

     :transform
     {"FaceURL" (get-in card [:card/faces (if transformed? 1 0) :png])
      "BackURL" (get BACK-URL (:card/layout card) (BACK-URL "normal"))
      "NumHeight" 1
      "NumWidth" 1
      "BackIsHidden" true})))


(defn card->Description
  "returns a description given a card layout
   transformed? is used for double sided cards and returns an object for the reverse"
  ([card]
   (card->Description card false))
  ([card transformed?]
   (case (:card/layout-category card)
     :normal
     (format "[b]%s[/b]\n\n%s" (:card/type-line card) (:card/oracle-text card))

     :split
     (format "[b]%s[/b]\n\n%s\n\n--------------------------\n\n[b]%s[/b]\n\n%s"
             (get-in card [:card/faces 0 :type-line])
             (get-in card [:card/faces 0 :oracle-text])
             (get-in card [:card/faces 1 :type-line])
             (get-in card [:card/faces 1 :oracle-text]))

     :double
     (let [face (if transformed? 1 0)]
       (format  "[b]%s[/b]\n\n%s"
                (get-in card [:card/faces face :type-line])
                (get-in card [:card/faces face :oracle-text]))))))


(defn tts-card->ContainedObject
  "returns a contained object dict for a TTS deck"
  ([tts-card]
   (tts-card->ContainedObject tts-card false))
  ([tts-card transformed?]
   (let [base-ContainedObject {"Name" "Card"
                               "Transform" {"posX" 0.0 "posY" 0.0 "posZ" 0.0
                                            "rotX" 0.0 "rotY" 180.0 "rotZ" 180.0
                                            "scaleX" 1.0 "scaleY" 1.0 "scaleZ" 1.0}
                               "Nickname" (get-in tts-card [:tts-card/card :card/name])
                               "Description" (card->Description (:tts-card/card tts-card) transformed?)}]
     (case (get-in tts-card [:tts-card/card :card/layout-category])
       (:normal :split)
       (assoc base-ContainedObject "CardID" (:tts-card/tts-id tts-card))

       :transform
       (if transformed?
         (assoc base-ContainedObject
                "CardID"
                (get-in tts-card [:tts-card/faces 1 :tts-id]))
         (assoc base-ContainedObject
                "CardID"
                (get-in tts-card [:tts-card/faces 0 :tts-id])
                "States"
                {"2" (tts-card->ContainedObject tts-card true)}))))))


(defn deck->tts-cards
  "Returns a list of tts-card in the deck, repeated for count
  the same card with multiple copies has the same id

  two faced cards come with 2 ids"
  [deck]
  (loop [tts-id 100 decklines (:deck/decklines deck) tts-cards []]
    (if (empty? decklines)
      tts-cards
      (let [deckline (first decklines)]
        (case (get-in deckline [:deckline/card :card/layout-category])
          (:normal :split)
          (recur (+ tts-id 100)
                 (rest decklines)
                 (->> #:tts-card{:tts-id tts-id
                                 :card (:deckline/card deckline)}
                      (repeat (:deckline/count deckline))
                      (concat tts-cards)))

          :transform
          (recur (+ tts-id 200)
                 (rest decklines)
                 (->> #:tts-card{:faces [{:tts-id tts-id}
                                         {:tts-id (+ tts-id 100)}]
                                 :card (:deckline/card deckline)}
                      (repeat (:deckline/count deckline))
                      (concat tts-cards))))))))


(defn tts-cards->CustomDeck
  "returns a map of card_id -> object_state"
  [tts-cards]
  (letfn [(reducer [acc tts-card]
            (case (get-in tts-card [:tts-card/card :card/layout-category])
              (:normal :split)
              (assoc acc
                     (str (/ (:tts-card/tts-id tts-card) 100))
                     (card->ObjectState (:tts-card/card tts-card)))

              :transform
              (assoc acc
                     (str (/ (get-in tts-card [:tts-card/faces 0 :tts-id]) 100))
                     (card->ObjectState (:tts-card/card tts-card))
                     (str (/ (get-in tts-card [:tts-card/faces 1 :tts-id]) 100))
                     (card->ObjectState (:tts-card/card tts-card) true))))]

    (reduce reducer {} tts-cards)))


(defn deck->tts-deck
  "returns a dict representing a tts deck"
  [deck]
  (let [tts-cards (deck->tts-cards deck)
        ContainedObjects (map tts-card->ContainedObject tts-cards)]
    {"ObjectStates" [{"Name" "DeckCustom"
                      "Nickname" (:deck/name deck)
                      "Description" (:deck/description deck)
                      "Transform" {"posX" 0.0 "posY" 1.0 "posZ" 0.0
                                   "rotX" 0.0 "rotY" 180.0 "rotZ" 180.0
                                   "scaleX" 1.0 "scaleY" 1.0 "scaleZ" 1.0}
                      "DeckIDs" (map #(get % "CardID") ContainedObjects)
                      "CustomDeck" (tts-cards->CustomDeck tts-cards)
                      "ContainedObjects" ContainedObjects}]}))


(defn write-tts-deck!
  [ttsdeck]
  (let [filename (format "%s.json" (sf/sanitize (get-in ttsdeck ["ObjectStates" 0 "Nickname"])))]
    (with-open [f (io/writer filename)]
      (spit filename (json/generate-string ttsdeck)))))
