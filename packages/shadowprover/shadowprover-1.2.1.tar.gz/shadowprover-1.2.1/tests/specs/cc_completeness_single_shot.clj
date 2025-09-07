 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*single-shot-completeness-test-1*"
 :description ""
 :assumptions {1 (Believes! a1 t0 P)
               2 (Believes! a1 t0 (if P Q))}
 :goal        (Believes! a1 t0 Q)}

 
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
{:name        "*single-shot-completeness-test-2*"
 :description "Bird Theorem and Jack"
 :assumptions {1 (Believes! a t P)
               2 (Believes! a t Q)
               3 (if (Believes! a t (and P Q)) (Believes! a t R))}
 :goal        (Believes! a t R)}



;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
{:name        "*single-shot-completeness-test-3*"
 :description "Equality within belief"
 :assumptions {
               1 (Believes! a t (Philosopher plato))
               2 (Believes! a t (= plato platon))
              }
 :goal   (Believes! a t (Philosopher platon))}


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
{:name        "*single-shot-completeness-test-4*"
 :description "Equality within belief and quantifier"
 :assumptions {
               1 (forall x (Believes! x t (Philosopher plato)))
               2 (Believes! a t (= plato platon))
              }
 :goal   (Believes! a t (Philosopher platon))}

 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
{:name        "*single-shot-completeness-test-4*"
 :description "Equality within belief and quantifier"
 :assumptions {
               1 (forall x (Believes! x t (Philosopher plato)))
               2 (forall x (Believes! x t (= plato platon)))
              }
 :goal   (Believes! a t (Philosopher platon))}


 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
{:name        "*single-shot-completeness-test-5*"
 :description "Equality within belief and quantifier"
 :assumptions {
               1 (if P (forall x (Believes! x t (Philosopher plato))))
               2 P
               3 (Believes! jack t (= plato platon))
              }
 :goal   (Believes! jack t (Philosopher platon))}



 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
{:name        "*single-shot-completeness-test-6*"
 :description "Equality within belief and quantifier"
 :assumptions {
               1 (if P (forall x (Believes! x t (Philosopher plato))))
               2 P
               3 (Believes! jack t (= plato platon))
               4  (if  (Believes! jack t (Philosopher platon))  (Believes! jack t (Wise platon)))
              }
 :goal   (Believes! jack t (Wise platon))}


 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
{:name        "*single-shot-completeness-test-7*"
 :description "Equality within belief and quantifier"
 :assumptions {
               1 (if P (forall x (Believes! x t (Philosopher plato))))
               2 P
               3 (Believes! jack t (= plato platon))
               4  (forall (x) (if  (Believes! x t (Philosopher platon))  (Believes! x t (Wise platon))))
              }
 :goal   (Believes! jack t (Wise platon))}


  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
{:name        "*single-shot-completeness-test-8*"
 :description "Equality within belief and quantifier"
 :assumptions {
               1 (Believes! jack t (Philosopher platon))
               4  (forall (y) (if  (Believes! jack t (Philosopher y))  (Believes! jack t (Wise y))))
              }
 :goal   (Believes! jack t (Wise platon))}


 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
{:name        "*single-shot-completeness-test-9*"
 :description "Equality within belief and quantifier"
 :assumptions {
               1 (if P (forall x (Believes! x t (Philosopher plato))))
               2 P
               3 (Believes! jack t (= plato platon))
               4  (forall (x y) (if  (Believes! x t (Philosopher y))  (Believes! x t (Wise y))))
              }
 :goal   (Believes! jack t (Wise platon))}



 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
{:name        "*single-shot-completeness-test-10*"
 :description "Equality within belief and quantifier"
 :assumptions {
               1 (if P (forall x (Believes! x t (Philosopher plato))))
               2 P
               3 (forall x (Believes! x t (= plato platon)))
               4 (forall (x y) (if  (Believes! x t (Philosopher y))  (Believes! x t (Wise y))))
              }
 :goal   (Believes! jack t (Wise platon))}


 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
{:name        "*single-shot-completeness-test-11*"
 :description "Equality within belief and quantifier"
 :assumptions {
               1 (if (linked a c) (forall x (Believes! x t (Philosopher plato))))
               2 (forall [x y z] (if (and (linked x y) (linked y z)) (linked x z)))
               3 (forall x (Believes! x t (= plato platon)))
               4 (forall (x y) (if  (Believes! x t (Philosopher y))  (Believes! x t (Wise y))))
               5 (linked a b)
               6 (linked a c)
              }
 :goal   (Believes! jack t (Wise platon))}


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
{:name        "*single-shot-completeness-test-12*"
 :description "Equality within belief and quantifier"
 :assumptions {
               1 (forall agent (if (Believes! agent t (linked a c) )(Believes! agent t (Philosopher plato))))
               2 (forall agent (Believes agent t (forall [x y z] (if (and (linked x y) (linked y z)) (linked x z)))))
               3 (forall x (Believes! x t (= plato platon)))
               4 (forall (x y) (if  (Believes! x t (Philosopher y))  (Believes! x t (Wise y))))
               5 (Believes! jack t (linked a b))
               6 (Believes! jack t (linked a c))
              }
 :goal    (Believes! jack t (Wise platon))}


 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
{:name        "*single-shot-completeness-test-13*"
 :description "Equality within belief and quantifier"
 :description ""
 :assumptions {1 (Believes! jack (Believes! superman t P))
                2 (Believes! jack (Believes! superman t (if P Q)))
               }
 :goal       (Believes! jack (Believes! superman t P))
 
 }

 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
{:name        "*single-shot-completeness-test-14*"
 :description "Equality within belief and quantifier"
 :description ""
 :assumptions {1 (Believes! jack (Believes! superman t0 P))
               2 (Believes! jack (Believes! superman t0 (if P Q)))
               3 (Believes! jack (= clark superman))
               }
 :goal        (Believes! jack (Believes! clark t0 Q))
 
 }

