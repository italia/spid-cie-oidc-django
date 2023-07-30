# EUDI Wallet Federation onboarding tutorial


Please follow these steps described below to have a fully working demo.
The sections identified with the prefix **[FedOp]** are related to the Federation operators that
accreditates the subordinates. The sections identified with the prefix **[User]** are 
related to the User that asks to get a specific Entity onboarded within the onboarding service.

## [FedOp] Configure you Trust Anchor

For demo purpose you can even import the dumps located in the [dumps](dumps) 
folder, containing a demo Trust Anchor setup.

## [User] Onboard your entity

Go to [the onboarding demo service](127.0.0.1:8000/onboarding/landing) and click
on the button `Register your entity`.

### [User] Fill the form

Fill the form field as show in the picture below.

![rp-onb](onb1.png)

Then click on the button `Submit`. If the validation of the Entity's configuration passes,
the user will be redirected to the onboarding status page, as shown below:

![rp-onb2](onb2.png)
 
Now the onboarding request is verified and accepted, now it requires an 
administrative validation from the Federation operators.

### [FedOp] enable the descendant

The admins of the platform opens the pending onboarding requests and after a 
checks selects all the ones that are eligible to be subordinates of this federation.

![rp-onb](onb3.png)

### [User] get the Entity Statement

The onboarding request appear as completed.

![rp-onb](onb4.png)

Then User connects to 
[the fetch endpoint](http://127.0.0.1:8000/fetch?sub=https://localhost:10000/OpenID4VP&anchor=http://127.0.0.1:8000)
and obtains the entity statement related to the onboarded Entity.

