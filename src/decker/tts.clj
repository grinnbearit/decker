(ns decker.tts
  (:require [clojure.java.io :as io]
            [cheshire.core :as json]
            [sanitize-filename.core :as sf]))


(def BACK-URL "http://cloud-3.steamusercontent.com/ugc/998016607072060763/7AFEF2CE9E7A7DB735C93CF33CC4C378CBF4B20D/")


(defn card->objectstate
  "returns an object state dict for a TTS deck"
  [card]
  {"FaceURL" (:card/png card)
   "BackURL" BACK-URL
   "NumHeight" 1
   "NumWidth" 1
   "BackIsHidden" true})


(defn card->description
  "returns a description given a card layout"
  [card]
  (format "[b]%s[/b]\n\n%s" (:card/type-line card) (:card/oracle-text card)))


(defn card->contained-object
  "returns a contained object dict for a TTS deck"
  [card-id card]
  {"Name" "Card"
   "Transform" {"posX" 0.0 "posY" 0.0 "posZ" 0.0
                "rotX" 0.0 "rotY" 180.0 "rotZ" 180.0
                "scaleX" 1.0 "scaleY" 1.0 "scaleZ" 1.0}
   "Nickname" (:card/name card)
   "Description" (card->description card)
   "CardID" card-id})


(defn card->ttscard
  "returns a map representing a stand alone tts card"
  [card]
  {"ObjectStates" [(card->objectstate card)]})


(defn explode-deck
  "Returns a list of [tts-id, card] in the deck, repeated for count
  the same card with multiple copies has the same id"
  [eddex decklines]
  (->>
   (map-indexed (fn [i deckline]
                  (->> [(* (inc i) 100)
                        (get-in eddex [(:deckline/code deckline)
                                       (:deckline/collector-number deckline)])]
                       (repeat (:deckline/count deckline))))
                decklines)
   (apply concat)))


(defn exploded-deck->custom-deck
  "returns a map of card_id -> object_state"
  [exploded-deck]
  (reduce (fn [acc [tts-id card]]
            (assoc acc (str (/ tts-id 100)) (card->objectstate card)))
          {}
          exploded-deck))


(defn exploded-deck->contained-objects
  "returns a list of contained-objects"
  [exploded-deck]
  (map (fn [[tts-id card]]
         (card->contained-object tts-id card))
       exploded-deck))


(defn deck->ttsdeck
  "returns a dict representing a tts deck"
  [eddex deck]
  (let [exploded-deck (explode-deck eddex (:deck/decklines deck))]
    (if (= (count exploded-deck) 1)
      (card->ttscard ((comp second first) exploded-deck))
      {"ObjectStates" [{"Name" "DeckCustom"
                        "Nickname" (:deck/name deck)
                        "Description" (:deck/description deck)
                        "Transform" {"posX" 0.0 "posY" 1.0 "posZ" 0.0
                                     "rotX" 0.0 "rotY" 180.0 "rotZ" 180.0
                                     "scaleX" 1.0 "scaleY" 1.0 "scaleZ" 1.0}
                        "DeckIDs" (map first exploded-deck)
                        "CustomDeck" (exploded-deck->custom-deck exploded-deck)
                        "ContainedObjects" (exploded-deck->contained-objects exploded-deck)}]})))


(defn write-ttsdeck!
  [ttsdeck]
  (let [filename (format "%s.json" (sf/sanitize (get-in ttsdeck ["ObjectStates" 0 "Nickname"])))]
    (with-open [f (io/writer filename)]
      (spit filename (json/generate-string ttsdeck)))))
