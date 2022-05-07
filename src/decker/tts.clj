(ns decker.tts
  (:require [clojure.java.io :as io]
            [cheshire.core :as json]
            [sanitize-filename.core :as sf]
            [decker.edition :as de]))


(def BACK-URL
  {"scheme" "http://cloud-3.steamusercontent.com/ugc/998016607072055936/0598975AB8EC26E8956D84F9EC73BBE5754E6C80/"
   "planar" "http://cloud-3.steamusercontent.com/ugc/998016607072060000/1713AE8643632456D06F1BBA962C5514DD8CCC76/"
   "normal" "http://cloud-3.steamusercontent.com/ugc/998016607072060763/7AFEF2CE9E7A7DB735C93CF33CC4C378CBF4B20D/"})


(defn card->objectstate
  "returns an object state dict for a TTS deck,
  flipped? is used for double sided cards and returns an object for the reverse"
  ([card]
   (card->objectstate card false))
  ([card flipped?]
   (case (de/layout->category (:card/layout card))
     (:normal :split)
     {"FaceURL" (:card/png card)
      "BackURL" (get BACK-URL (:card/layout card) (BACK-URL "normal"))
      "NumHeight" 1
      "NumWidth" 1
      "BackIsHidden" true}

     :double
     {"FaceURL" (if flipped?
                  (get-in card [:card/faces 1 :png])
                  (get-in card [:card/faces 0 :png]))
      "BackURL" (get BACK-URL (:card/layout card) (BACK-URL "normal"))
      "NumHeight" 1
      "NumWidth" 1
      "BackIsHidden" true})))


(defn card->description
  "returns a description given a card layout
   flipped? is used for double sided cards and returns an object for the reverse"
  ([card]
   (card->description card false))
  ([card flipped?]
   (case (de/layout->category (:card/layout card))
     :normal
     (format "[b]%s[/b]\n\n%s" (:card/type-line card) (:card/oracle-text card))

     :split
     (format "[b]%s[/b]\n\n%s\n\n--------------------------\n\n[b]%s[/b]\n\n%s"
             (get-in card [:card/faces 0 :type-line])
             (get-in card [:card/faces 0 :oracle-text])
             (get-in card [:card/faces 1 :type-line])
             (get-in card [:card/faces 1 :oracle-text]))

     :double
     (let [face (if flipped? 1 0)]
       (format  "[b]%s[/b]\n\n%s"
                (get-in card [:card/faces face :type-line])
                (get-in card [:card/faces face :oracle-text]))))))


(defn card->contained-object
  "returns a contained object dict for a TTS deck"
  ([tts-id card]
   (card->contained-object tts-id card false))
  ([tts-id card flipped?]
   (cond->  {"Name" "Card"
             "Transform" {"posX" 0.0 "posY" 0.0 "posZ" 0.0
                          "rotX" 0.0 "rotY" 180.0 "rotZ" 180.0
                          "scaleX" 1.0 "scaleY" 1.0 "scaleZ" 1.0}
             "Nickname" (:card/name card)
             "Description" (card->description card flipped?)
             "CardID" tts-id}

     (and (= (de/layout->category (:card/layout card)) :double)
          (not flipped?))
     (assoc "States" {"2" (assoc (card->contained-object tts-id card true)
                                 "CustomDeck" {(str (/ tts-id 100))
                                               (card->objectstate card true)})}))))


(defn card->ttscard
  "returns a map representing a stand alone tts card"
  [card]
  (if (= (de/layout->category (:card/layout card))
         :flipped)
    {"ObjectStates" [(card->objectstate card)
                     (card->objectstate card true)]}
    {"ObjectStates" [(card->objectstate card)]}))


(defn explode-deck
  "Returns a list of [tts-id, card] in the deck, repeated for count
  the same card with multiple copies has the same id"
  [decklines]
  (->>
   (map-indexed (fn [i deckline]
                  (->> [(* (inc i) 100)
                        (:deckline/card deckline)]
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
  [deck]
  (let [exploded-deck (explode-deck (:deck/decklines deck))]
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
