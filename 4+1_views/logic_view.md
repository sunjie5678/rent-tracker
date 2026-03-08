flowchart TB
    start(["start"]) --> step1["User navigates to Payments page"]
    step1 --> step2["User clicks New Payment button"]
    step2 --> step3["User fills payment form"]
    step3 --> checkForm{"Form validated?"}
    checkForm -- Yes --> step4["PaymentFactory creates Payment object"]
    step4 --> step5["PaymentRepository saves to database"]
    step5 --> stop(["stop"])
flowchart TB
    start(["start"]) -->  step6["User navigates to Payment Detail page"]
    step6 --> step7["User clicks Allocate Payment link"]
    step7 --> checkCharges{"Outstanding charges exist?"}
    checkCharges -- Yes --> step8["User selects allocation method"]
    step8 --> checkManual{"Manual Allocation?"}
    checkManual -- Yes --> step9["User selects Rent Charge"]
    step9 --> step10["User enters allocation amount"]
    step10 --> checkAllocation{"Allocation valid?"}
    checkAllocation -- Yes --> step11["PaymentService.allocate_payment()"]
    step11 --> step12["Create PaymentAllocation record"]
    step12 --> step13["Update RentCharge status"]
    step13 --> step14["Display success message"]
    step14 --> stop(["stop"])
flowchart TB
    start(["start"]) -->  step6["User navigates to Payment Detail page"]
    step6 --> step17["User clicks Auto-Allocate button for payment"]
    step17 --> step18["PaymentService.auto_allocate_payment()"]
    step18 --> step19["System allocates to oldest charges first"]
    step19 --> step20["Create PaymentAllocation records"]
    step20 --> step21["Update all affected RentCharge statuses"]
    step21 --> step22["Display success message with count"]
    step22 --> stop(["stop"])