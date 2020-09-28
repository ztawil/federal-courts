-- Unsuccessful Nomination By President
-- 
SELECT
    LEFT(president, strpos(president, ' (')) AS president,
    congress_start_year,
    count(*)
FROM unsuccessful_nomination
WHERE congress_start_year > 1900
GROUP BY president, congress_start_year
ORDER BY congress_start_year, president;



SELECT 
    unsuccessful_nomination.president AS unsuccessful_nomination_president,
    appointment.party_of_appointing_president AS appointment_party_of_appointing_president,
    unsuccessful_nomination.congress_start_year AS unsuccessful_nomination_congress_start_year,
    count(1) AS count 
FROM unsuccessful_nomination
JOIN (SELECT appointing_president, party_of_appointing_president FROM appointment GROUP BY appointing_president, party_of_appointing_president) AS appointment
    ON appointment.appointing_president = unsuccessful_nomination.president
GROUP BY unsuccessful_nomination.president, appointment.party_of_appointing_president, unsuccessful_nomination.congress_start_year
ORDER BY unsuccessful_nomination.congress_start_year, min(unsuccessful_nomination.nomination_date), appointment.party_of_appointing_president, unsuccessful_nomination.president