-- Unsuccessful Nomination By President
-- Have an issue with president's appointint in January and the year showing up as the next president's
SELECT
    LEFT(president, position(' (' in president)) AS president,
    congress_start_year,
    count(*)
FROM unsuccessful_nomination
WHERE congress_start_year > 1900
GROUP BY president, congress_start_year
ORDER BY congress_start_year, president;