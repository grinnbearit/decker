(ns decker.tts-test
  (:use midje.sweet
        decker.tts))


(facts
 "card -> objectstate"
 (card->objectstate #:card{:png "png-url"
                           :layout "planar"})
 => {"FaceURL" "png-url"
     "BackURL" (BACK-URL "planar")
     "NumHeight" 1
     "NumWidth" 1
     "BackIsHidden" true}


 (card->objectstate #:card{:png "png-url"
                           :layout "split"})
 => {"FaceURL" "png-url"
     "BackURL" (BACK-URL "normal")
     "NumHeight" 1
     "NumWidth" 1
     "BackIsHidden" true}


 (card->objectstate #:card{:faces [{:png "png-url-1"}
                                   {:png "png-url-2"}]
                           :layout "double_faced_token"})
 => {"FaceURL" "png-url-1"
     "BackURL" (BACK-URL "normal")
     "NumHeight" 1
     "NumWidth" 1
     "BackIsHidden" true}


 (card->objectstate #:card{:faces [{:png "png-url-1"}
                                   {:png "png-url-2"}]
                           :layout "double_faced_token"}
                    true)
 => {"FaceURL" "png-url-2"
     "BackURL" (BACK-URL "normal")
     "NumHeight" 1
     "NumWidth" 1
     "BackIsHidden" true})


(facts
 "card -> description"

 (card->description #:card{:type-line "type line"
                           :oracle-text "oracle text"
                           :layout "normal"})
 => (str "[b]type line[/b]"
         "\n\n"
         "oracle text")


 (card->description #:card{:layout "split"
                           :faces [{:type-line "type line 1"
                                    :oracle-text "oracle text 1"}
                                   {:type-line "type line 2"
                                    :oracle-text "oracle text 2"}]})
 => (str "[b]type line 1[/b]"
         "\n\n"
         "oracle text 1"
         "\n\n"
         "--------------------------"
         "\n\n"
         "[b]type line 2[/b]"
         "\n\n"
         "oracle text 2")


 (card->description #:card{:layout "double_faced_token"
                           :faces [{:type-line "type line 1"
                                    :oracle-text "oracle text 1"}
                                   {:type-line "type line 2"
                                    :oracle-text "oracle text 2"}]})
 => (str "[b]type line 1[/b]"
         "\n\n"
         "oracle text 1")


 (card->description #:card{:layout "double_faced_token"
                           :faces [{:type-line "type line 1"
                                    :oracle-text "oracle text 1"}
                                   {:type-line "type line 2"
                                    :oracle-text "oracle text 2"}]}
                    true)
 => (str "[b]type line 2[/b]"
         "\n\n"
         "oracle text 2"))


(facts
 "card -> contained object"

 (let [card #:card{:name "card-name"
                   :layout "normal"}]

   (card->contained-object 100 card)
   => {"Name" "Card",
       "Transform" {"posX" 0.0 "posY" 0.0 "posZ" 0.0
                    "rotX" 0.0 "rotY" 180.0 "rotZ" 180.0
                    "scaleX" 1.0 "scaleY" 1.0, "scaleZ" 1.0}
       "Nickname" "card-name"
       "Description" "card-description"
       "CardID" 100}

   (provided
    (card->description card false) => "card-description"))


 (let [card #:card{:name "card-name"
                   :layout "double_faced_token"}]

   (card->contained-object 100 card)
   => {"Name" "Card",
       "Transform" {"posX" 0.0 "posY" 0.0 "posZ" 0.0
                    "rotX" 0.0 "rotY" 180.0 "rotZ" 180.0
                    "scaleX" 1.0 "scaleY" 1.0, "scaleZ" 1.0}
       "Nickname" "card-name"
       "Description" "card-description-1"
       "CardID" 100
       "States" {"2" {"Name" "Card",
                      "Transform" {"posX" 0.0 "posY" 0.0 "posZ" 0.0
                                   "rotX" 0.0 "rotY" 180.0 "rotZ" 180.0
                                   "scaleX" 1.0 "scaleY" 1.0, "scaleZ" 1.0}
                      "Nickname" "card-name"
                      "Description" "card-description-2"
                      "CardID" 100
                      "CustomDeck" {"1" "flipped-state"}}}}

   (provided
    (card->description card false) => "card-description-1"
    (card->description card true) => "card-description-2"
    (card->objectstate card true) => "flipped-state")))


(facts
 "card -> ttscard"

 (let [card "card"]

   (card->ttscard card)
   => {"ObjectStates" ["card-objectstate"]}

   (provided
    (card->objectstate card) => "card-objectstate")))


(facts
 "explode deck"

 (explode-deck [#:deckline{:count 2 :card #:card{:name "card-1"}}
                #:deckline{:count 1 :card #:card{:name "card-2"}}])
 => [[100 #:card{:name "card-1"}]
     [100 #:card{:name "card-1"}]
     [200 #:card{:name "card-2"}]])


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

 (deck->ttsdeck #:deck{:name "deck" :decklines [#:deckline{:card #:card{:name "card-1"}}]})
 => "tts-card"

 (provided
  (explode-deck [#:deckline{:card #:card{:name "card-1"}}])
  => [[100 #:card{:name "card-1"}]]

  (card->ttscard #:card{:name "card-1"})
  => "tts-card")

 (deck->ttsdeck #:deck{:name "deck"
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
  (explode-deck [#:deckline{:name "card-1"}
                 #:deckline{:name "card-2"}])
  => [[100 #:card{:name "card-1"}]
      [200 #:card{:name "card-2"}]]

  (exploded-deck->custom-deck [[100 #:card{:name "card-1"}]
                               [200 #:card{:name "card-2"}]])
  => "custom-deck"

  (exploded-deck->contained-objects [[100 #:card{:name "card-1"}]
                                     [200 #:card{:name "card-2"}]])
  => "contained-objects"))
