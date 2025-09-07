
 {
    :name "DCEC"
    :description "DCEC" 
    
    :schema {

        :R4 {
            :name "R4"
            :inputs [(Knows! ?a ?t ?P)]
            :output [?P]
        }

        
        :R_K_B {
            :name "Knowledge to belief"
            :inputs [(Knows! ?a ?t ?P)]
            :output (Believes! ?a ?t ?P)
        }
        :Common_to_K1 {
            :name "Common to Knowledge 1"
            :inputs [(Common! ?t ?P)]
            :output (Knows! ?a ?t ?P)

        }
        :Common_to_K2 {
            :name "Common to Knowledge 2 "
            :inputs [(Common! ?t ?P)]
            :output (Knows! ?a t (Knows! ?a ?t ?P))

        }
        :Perception_to_Knowledge {
            :name "Common to Knowledge "
            :inputs [(Perceives! ?a ?t ?P)]
            :output (Knows! ?a ?t ?P)

        }    
    }
}