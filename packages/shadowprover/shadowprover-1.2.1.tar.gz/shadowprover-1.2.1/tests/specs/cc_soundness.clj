{:name        "*single-shot-soundness-1*"
 :description "kicking the tires"
 :assumptions {1 A}
 :goal        (or P Q)
 }

{:name        "*single-shot-soundness-2*"
 :description "Referential opacity should be satisfied"
 :assumptions {1 (not (Believes! a now (= morning_star evening_star)))
               2 (= morning_star evening_star)
               3 (Believes! a now (= morning_star morning_star))}
 :goal        (and P (not P))
 }


 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
{:name        "*single-shot-soundness-3*"
 :description "Equality within belief and quantifier"
 :assumptions {
               1 (forall x (Believes! x t (Philosopher plato)))
               2 (= plato platon)
              }
 :goal   (Believes! a t (Philosopher platon))}


  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
{:name        "*single-shot-completeness-test-13*"
 :description "Equality within belief and quantifier"
 :description ""
 :assumptions {1 (Believes! jack (Believes! superman t0 P))
               2 (Belives! jack (Believes! superman t0 (if P Q)))
               }
 :goal        (Believes! superman t0 Q)
 
 }

