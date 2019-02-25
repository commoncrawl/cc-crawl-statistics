includes internationalized country code top-level domain (IDN ccTLD)

there is some confusion about the definition of (top-level) domains, see [1].
  And as it depends on public suffix lists there may be differences how
  a library (or a version of) splits a host into <tld,domain,subdomain>.

`s3.amazonaws.com` is a public suffix and `commoncrawl.s3.amazonaws.com` is a private domain,
but `amazonaws.com` is also private domain and `com` is a public suffix   


 https://github.com/google/guava/wiki/InternetDomainNameExplained
 
https://en.wikipedia.org/wiki/Public_Suffix_List
 https://publicsuffix.org/
 https://www.iana.org/domains/root/db
 https://en.wikipedia.org/wiki/Second-level_domain
 
