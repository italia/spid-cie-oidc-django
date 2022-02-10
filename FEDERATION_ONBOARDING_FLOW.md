

onboarding

1. il rappr. legale di un ente/org accede mediante SPID o CIE
2. diviene riconoscibiel come affiliato di della org e gli vengono dati i privilegi per operare per conto di quella org

3. accede al form di sottomissione di una entità di federazione, compila i seguenti campi REQUIRED:
    1. Organization Name
    2. identificativo univoco dell'entità (url) della istanza in produzione/stage
    3. IPA code o VAT number (determina se il partecipante è public o private)
    4. jwks di tipo JSON List[array]
    5. almeno un contatto (può aggiungere quanti contatti desidera per un massimo di 6)

4. validazioni:
    1. Organizazion Name -> nessun validazione
    2. validazione della entity configuration:
        1. download dello statement self-signed dall'ente
        2. analisi della struttura (json-schema)
        3. analisi della presenza del trust anchor all'interno del claim authority_hints, al quale il sistema di onboarding è riferito
        4. verifica della firma self-signed
        5. batteria di test sui claims json
