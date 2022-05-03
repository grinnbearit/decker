(ns decker.tts-test
  (:use midje.sweet
        decker.tts))


(facts
 "card -> objectstate"
 (card->objectstate {:card/png "png-url"})
 =>   {"FaceURL" "png-url"
       "BackURL" BACK-URL
       "NumHeight" 1
       "NumWidth" 1
       "BackIsHidden" true})


(facts
 "card -> description"

 (card->description #:card{:type-line "type line"
                           :oracle-text "oracle text"})
 => "[b]type line[/b]\n\noracle text")



(facts
 "card -> contained object"

 (let [card #:card{:name "card-name"}]

   (card->contained-object 100 card)
   => {"Name" "Card",
       "Transform" {"posX" 0.0 "posY" 0.0 "posZ" 0.0
                    "rotX" 0.0 "rotY" 180.0 "rotZ" 180.0
                    "scaleX" 1.0 "scaleY" 1.0, "scaleZ" 1.0}
       "Nickname" "card-name"
       "Description" "card-description"
       "CardID" 100}

   (provided
    (card->description card) => "card-description")))


(facts
 "card -> ttscard"

 (let [card "card"]

   (card->ttscard card)
   => {"ObjectStates" ["card-objectstate"]}

   (provided
    (card->objectstate card) => "card-objectstate")))


(facts
 "explode deck"

 (let [eddex {"rqs" {"1" #:card{:name "card-1"}
                     "2" #:card{:name "card-2"}}}]

   (explode-deck eddex [#:deckline{:name "card-1" :code "rqs" :collector-number "1" :count 2}
                        #:deckline{:name "card-2" :code "rqs" :collector-number "2" :count 1}])
   => [[100 #:card{:name "card-1"}]
       [100 #:card{:name "card-1"}]
       [200 #:card{:name "card-2"}]]))


(facts
 "exploded deck -> custom deck"

 (exploded-deck->custom-deck [[100 #:card{:name "card-1"}]
                              [100 #:card{:name "card-1"}]
                              [200 #:card{:name "card-2"}]])
 => {"1" "object-1"
     "2" "object-2"}

 (provided
  (card->objectstate #:card{:name "card-1"})
  => "object-1"

  (card->objectstate #:card{:name "card-2"})
  => "object-2"))


(facts
 "exploded deck -> contained objects"

 (exploded-deck->contained-objects [[100 #:card{:name "card-1"}]
                                    [200 #:card{:name "card-2"}]])
 => ["contained-1"
     "contained-2"]

 (provided
  (card->contained-object 100 #:card{:name "card-1"})
  => "contained-1"

  (card->contained-object 200 #:card{:name "card-2"})
  => "contained-2"))


(facts
 "deck -> ttsdeck"

 (deck->ttsdeck "EDDEX" #:deck{:name "deck" :decklines [#:deckline{:name "card-1"}]})
 => "tts-card"

 (provided
  (explode-deck "EDDEX" [#:deckline{:name "card-1"}])
  => [[100 #:card{:name "card-1"}]]

  (card->ttscard #:card{:name "card-1"})
  => "tts-card")

 (deck->ttsdeck "EDDEX" #:deck{:name "deck"
                               :description "description"
                               :decklines [#:deckline{:name "card-1"}
                                           #:deckline{:name "card-2"}]})
 => {"ObjectStates" [{"Name" "DeckCustom"
                      "Nickname" "deck"
                      "Description" "description"
                      "Transform" {"posX" 0.0 "posY" 1.0 "posZ" 0.0
                                   "rotX" 0.0 "rotY" 180.0 "rotZ" 180.0
                                   "scaleX" 1.0 "scaleY" 1.0 "scaleZ" 1.0}
                      "DeckIDs" [100 200]
                      "CustomDeck" "custom-deck"
                      "ContainedObjects" "contained-objects"}]}

 (provided
  (explode-deck "EDDEX" [#:deckline{:name "card-1"}
                         #:deckline{:name "card-2"}])
  => [[100 #:card{:name "card-1"}]
      [200 #:card{:name "card-2"}]]

  (exploded-deck->custom-deck [[100 #:card{:name "card-1"}]
                               [200 #:card{:name "card-2"}]])
  => "custom-deck"

  (exploded-deck->contained-objects [[100 #:card{:name "card-1"}]
                                     [200 #:card{:name "card-2"}]])
  => "contained-objects"))
