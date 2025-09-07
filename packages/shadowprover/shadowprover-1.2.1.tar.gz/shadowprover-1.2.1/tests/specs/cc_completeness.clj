
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*cognitive-calculus-completeness-test-1*"
 :description "Knowledge of P implies P"
 :assumptions {1 (Knows! a1 t1 P)}
 :goal        P}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*cognitive-calculus-completeness-test-2*"
 :description "Knowledge of P implies P or Q"
 :assumptions {1 (Knows! a1 t1 P)}
 :goal        (or P Q)}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
{:name        "*cognitive-calculus-completeness-test-3*"
 :description "Knowledge to belief"
 :assumptions {1 (Knows! a1 now P)}
 :goal        (Believes! a1 now P)}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
{:name        "*cognitive-calculus-completeness-test-4*"
 :description "Knowledge to belief"
 :assumptions {1 (Knows! a1 now P)}
 :goal        (Believes! a1 now (or P Q))}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
{:name        "*cognitive-calculus-completeness-test-5*"
 :description "Knowledge to belief"
 :assumptions {1 (Knows! a1 now (and P Q))}
 :goal        (Believes! a1 now (or P Q))}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
{:name        "*cognitive-calculus-completeness-test-6*"
 :description "Knowledge to belief"
 :assumptions {1 (Knows! a1 now (or P Q))}
 :goal        (Believes! a1 now (or Q P))}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
{:name  "*cognitive-calculus-completeness-test-7*"
 :description "Interactions between modals"
 :assumptions {:1 (Knows! b t1 P)
               :2 (if (Believes! b t1 (or (or (or S P) R) Q)) W)}
 :goal P}

 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
{:name  "*cognitive-calculus-completeness-test-8*"
 :description "Interactions between modals"
 :assumptions {:1 (Knows! b t1 P)
               :2 (if (Believes! b t1 (or (or (or S P) R) Q)) W)}
 :goal W}

  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
{:name  "*cognitive-calculus-completeness-test-9*"
 :description "Interactions between modals"
 :assumptions {:1 (Knows! b t1 P)
               :2 (if (Believes! b t1 (or (or (or S P) R) Q)) 
               W)
               
               :3 (Attention! (Believes! b t1 (or (or (or S P) R) Q)) )
               :4 (Attention! (Believes! b t1 P ))
               :5 (Attention! (Believes! b t1 (or S P) ))
               :6 (Attention! (Believes! b t1 (or (or S P) R)))
               :7 (Attention! (Believes! b t1 (or (or (or S P) R) Q))) 
                
                }
 :goal (or V W)}

 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*cognitive-calculus-completeness-test-10*"
 :description "Interactions between modals"
 :assumptions {1 (Believes! a1 t0 P)
               2 (Believes! a1 t0 (if P Q))}
 :goal        (Believes! a1 t0 Q)}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*cognitive-calculus-completeness-test-11*"
 :description "Bird Theorem and Jack"
 :assumptions {1 (if (exists (?X) (if (Bird ?X) (forall (?Y) (Bird ?Y))))
                   (Knows! jack t0 BirdTheorem))}
 :goal        (Knows! jack t0 BirdTheorem)}


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
{:name        "*cognitive-calculus-completeness-test-12*"
 :description "Bird Theorem and Jack"
 :assumptions {1 (Believes! a t P)
               2 (Believes! a t Q)
               3 (if (Believes! a t (and P Q)) (Knows! a t R))}
 :goal        R}

{:name        "*cognitive-calculus-completeness-test-13*"
 :description "dt5"
 :assumptions {1 (Knows! a1 t1 (if H (and E D)))
               2 (Knows! a1 t1 (Knows! a2 t2 (if (or E My) R)))
               3 (Knows! a1 t1 (Knows! a2 t2 (Knows! a3 t2 (if Ma (not R)))))
               
               4 (Attention! (if H (and E D)) )
               5 (Attention! (if (or E My) R)) 
               6 (Attention! (if Ma (not R) ))

               }
 :goal        (if H (not Ma))}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*cognitive-calculus-completeness-test-14*"
 :description "dt6"
 :assumptions {1 (and P (Knows! a t0 Q))}
 :goal        Q}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*cognitive-calculus-completeness-test-15*"
 :description "dt6.a"
 :assumptions {1 (and P (Knows! a t0 Q))}
 :goal        (and P Q)}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*cognitive-calculus-completeness-test-16*"
 :description "dt6.a"
 :assumptions {1 (and P (Knows! a t0 Q))}
 :goal        (or P Q)}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*cognitive-calculus-completeness-test-17*"
 :description "dt7"
 :assumptions {1 (and P (Knows! a now (and Q (Knows! b now R2))))
               2 (and P (Knows! a now (and Q (Knows! b now R1))))

               }
 :goal        (and R1 R2)}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*cognitive-calculus-completeness-test-18*"
 :description "dt8"
 :assumptions {1 P
               2 (if P (Knows! a now Q))}
 :goal        Q}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*cognitive-calculus-completeness-test-19*"
 :description "dt10"
 :assumptions {1 (or (Knows! a now P) (Knows! b now P))}
 :goal        P}


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*cognitive-calculus-completeness-test-20a*"
 :description "dt11.a"
 :assumptions {1 (if P (Knows! b now (and (Knows! c t1 Q1) (Knows! c t2 Q2))))
               2 (or (Knows! a now P) (Knows! b now P))
               3 (Attention! P)
               4 (Attention! (Knows! b now (and (Knows! c t1 Q1) (Knows! c t2 Q2))))
               5 (Attention!  (and (Knows! c t1 Q1) (Knows! c t2 Q2)))
                6 (Attention! (Knows! c t1 Q1))
               }
 :goal        Q1}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*cognitive-calculus-completeness-test-20b*"
 :description "dt11.a"
 :assumptions {1 (if P (Knows! b now (and (Knows! c t1 Q1) (Knows! c t2 Q2))))
               2 (or (Knows! a now P) (Knows! b now P))
                    3 (Attention! P)
               4 (Attention! (Knows! b now (and (Knows! c t1 Q1) (Knows! c t2 Q2))))
               5 (Attention!  (and (Knows! c t1 Q1) (Knows! c t2 Q2)))
                6 (Attention! (Knows! c t1 Q1)) 
                7 (Attention! (Knows! c t2 Q2)) 
               }
 :goal        (and Q1 Q2)}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*cognitive-calculus-completeness-test-21*"
 :description "dt15"
 :assumptions {1 (if P
                   (Knows! jack now (not (exists (X) (if (Bird X) (forall (Y) (Bird X)))))))}
 :goal        (not P)}

 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*cognitive-calculus-completeness-test-22*"
 :description "Bird Theorem and Jack"
 :assumptions {1 (if (exists (?X) (if (Bird ?X) (forall (?Y) (Bird ?Y))))
                   (Knows! jack t0 BirdTheorem))}
 :goal        (Knows! jack t0 BirdTheorem)}

 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*cognitive-calculus-completeness-test-23*"
 :description "Bird Theorem and Jack"
 :assumptions {1 (if (exists (?X) (if (Bird ?X) (forall (?Y) (Bird ?Y))))
                   (Knows! jack t0 BirdTheorem))}
 :goal        (Knows! jack t0 BirdTheorem)}

 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*cognitive-calculus-completeness-test-24*"
 :description "dt10"
 :assumptions {:1 (Common! now P)}
 :goal        (Knows! a now P)}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*cognitive-calculus-completeness-test-25*"
 :description "from licato's paper?"
 :assumptions {1 (Knows! a t (or (isExit A) (isExit B)))


               2 (Perceives! a t (not (isExit A)))}
 :goal        (Knows! a t (isExit B))}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
{:name        "*cognitive-calculus-completeness-test-26*"
 :description "universal intro inside a knows"
 :assumptions {1 (forall (?x) (if (P ?x) (Knows! ?x t U)))
               2 (P a)}

 :goal        (Knows! a t U)}