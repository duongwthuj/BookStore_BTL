param(
  [string]$ApiUrl = "http://localhost:8000/api"
)

$ErrorActionPreference = "Stop"

function Invoke-Json {
  param(
    [Parameter(Mandatory=$true)][ValidateSet('GET','POST')] [string]$Method,
    [Parameter(Mandatory=$true)] [string]$Path,
    [Parameter(Mandatory=$false)] $Body = $null,
    [Parameter(Mandatory=$false)] $Headers = $null
  )

  $uri = "$ApiUrl$Path"
  try {
    if ($Method -eq 'GET') {
      if ($Headers) {
        return Invoke-RestMethod -Method Get -Uri $uri -Headers $Headers -TimeoutSec 30
      }
      return Invoke-RestMethod -Method Get -Uri $uri -TimeoutSec 30
    }

    $json = if ($null -eq $Body) { "{}" } else { $Body | ConvertTo-Json -Depth 10 }
    if ($Headers) {
      return Invoke-RestMethod -Method Post -Uri $uri -Headers $Headers -ContentType "application/json" -Body $json -TimeoutSec 30
    }
    return Invoke-RestMethod -Method Post -Uri $uri -ContentType "application/json" -Body $json -TimeoutSec 30
  } catch {
    $responseText = $null
    try {
      if ($_.Exception.Response -and $_.Exception.Response.GetResponseStream()) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseText = $reader.ReadToEnd()
      }
    } catch {}

    $msg = "[$Method $uri] failed: $($_.Exception.Message)"
    if ($responseText) { $msg += "`nResponse: $responseText" }
    Write-Warning $msg
    return $null
  }
}

function Ensure-Created {
  param(
    [Parameter(Mandatory=$true)] [string]$Path,
    [Parameter(Mandatory=$true)] $Items,
    [Parameter(Mandatory=$true)] [string]$Key,
    [Parameter(Mandatory=$false)] $Headers = $null
  )

  foreach ($item in $Items) {
    Write-Host "Creating $Path $($item.$Key)..." -ForegroundColor Cyan
    Invoke-Json -Method POST -Path $Path -Body $item -Headers $Headers | Out-Null
  }
}

function Index-ByName {
  param(
    [Parameter(Mandatory=$true)] $List
  )
  $items = $List
  if ($null -ne $List -and ($List.PSObject.Properties.Name -contains 'results')) {
    $items = $List.results
  }

  $map = @{}
  foreach ($item in $items) {
    if ($item.name) {
      $map[$item.name] = $item
    }
  }
  return $map
}

Write-Host "=== Seeding BookStore Data (Windows/PowerShell) ===" -ForegroundColor Green
Write-Host "API: $ApiUrl" -ForegroundColor DarkGray

function Get-AccessToken {
  param(
    [Parameter(Mandatory=$true)][string]$Email,
    [Parameter(Mandatory=$true)][string]$Password
  )

  $registerBody = @{
    username = "seed_user"
    email = $Email
    password = $Password
    password_confirm = $Password
    first_name = "Seed"
    last_name = "User"
    phone = "0000000000"
  }

  # Register may fail if the user already exists; that's OK.
  Invoke-Json -Method POST -Path "/auth/register/" -Body $registerBody | Out-Null

  $loginBody = @{ email = $Email; password = $Password }
  $login = Invoke-Json -Method POST -Path "/auth/login/" -Body $loginBody
  if (-not $login -or -not $login.access) {
    throw "Login failed. Cannot obtain JWT access token."
  }
  return [string]$login.access
}

$seedEmail = "seed@example.com"
$seedPassword = "SeedPassw0rd!"
$accessToken = Get-AccessToken -Email $seedEmail -Password $seedPassword
$authHeaders = @{ Authorization = "Bearer $accessToken" }

# Smoke check
$health = Invoke-Json -Method GET -Path "/books/" -Headers $authHeaders
if ($null -eq $health) {
  throw "API is not reachable at $ApiUrl. Make sure Docker Compose is up and API Gateway is running on http://localhost:8000"
}

# 1) Categories (ASCII-only to avoid encoding issues on Windows PowerShell 5.1)
$categories = @(
  @{ name = "Van hoc"; description = "Fiction and literature" },
  @{ name = "Kinh te"; description = "Business and economics" },
  @{ name = "Ky nang song"; description = "Self-help and personal development" },
  @{ name = "Thieu nhi"; description = "Kids books" },
  @{ name = "Cong nghe"; description = "Technology and programming" }
)
Ensure-Created -Path "/categories/" -Items $categories -Key "name" -Headers $authHeaders

$categoryList = Invoke-Json -Method GET -Path "/categories/" -Headers $authHeaders
# categories endpoint returns nested roots; we only create roots so direct mapping works
$categoryByName = Index-ByName -List $categoryList

# 2) Collections
$collections = @(
  @{ name = "Best sellers"; description = "Top selling books"; is_active = $true },
  @{ name = "New arrivals"; description = "Newly released books"; is_active = $true },
  @{ name = "Discount"; description = "Books on promotion"; is_active = $true }
)
Ensure-Created -Path "/collections/" -Items $collections -Key "name" -Headers $authHeaders

$collectionList = Invoke-Json -Method GET -Path "/collections/" -Headers $authHeaders
$collectionByName = Index-ByName -List $collectionList

# 3) Shipping methods
$shippingMethods = @(
  @{ name = "Express"; fee = 30000; estimated_days = 2; free_ship_threshold = 500000 },
  @{ name = "Economy"; fee = 15000; estimated_days = 5; free_ship_threshold = 300000 }
)
Ensure-Created -Path "/shipping/methods/" -Items $shippingMethods -Key "name" -Headers $authHeaders

# 4) Coupons
$coupons = @(
  @{ code = "WELCOME10"; discount_type = "percent"; discount_value = 10; min_order = 100000; max_uses = 1000; is_active = $true },
  @{ code = "FREESHIP"; discount_type = "fixed"; discount_value = 30000; min_order = 200000; max_uses = 500; is_active = $true }
)
Ensure-Created -Path "/coupons/" -Items $coupons -Key "code" -Headers $authHeaders

# 5) Books (10+ records)
function Get-CategoryId([string]$name) {
  if (-not $categoryByName.ContainsKey($name)) { throw "Category not found: $name" }
  return [int]$categoryByName[$name].id
}

function Get-CollectionIds([string[]]$names) {
  $ids = @()
  foreach ($n in $names) {
    if ($collectionByName.ContainsKey($n)) {
      $ids += [int]$collectionByName[$n].id
    }
  }
  return $ids
}

$books = @(
  @{ title="Dac Nhan Tam"; author="Dale Carnegie"; description="Classic book about communication and understanding people."; price=86000; stock=100; category_name="Ky nang song"; collection_names=@("Best sellers"); isbn="9786043651249"; publisher="Tong Hop"; published_date="2020-05-01"; pages=320; cover_image="https://placehold.co/300x450?text=Dac+Nhan+Tam" },
  @{ title="The Alchemist"; author="Paulo Coelho"; description="A simple story about pursuing dreams and finding your treasure."; price=79000; stock=80; category_name="Van hoc"; collection_names=@("Best sellers","New arrivals"); isbn="9786043651256"; publisher="Van Hoc"; published_date="2019-09-15"; pages=228; cover_image="https://placehold.co/300x450?text=The+Alchemist" },
  @{ title="Sapiens: A Brief History of Humankind"; author="Yuval Noah Harari"; description="From the stone age to the AI age: a story of humankind."; price=299000; stock=50; category_name="Kinh te"; collection_names=@("New arrivals"); isbn="9786043651263"; publisher="Tri Thuc"; published_date="2021-01-10"; pages=560; cover_image="https://placehold.co/300x450?text=Sapiens" },
  @{ title="Clean Code"; author="Robert C. Martin"; description="A Handbook of Agile Software Craftsmanship."; price=450000; stock=30; category_name="Cong nghe"; collection_names=@("Best sellers"); isbn="9780132350884"; publisher="Prentice Hall"; published_date="2008-08-11"; pages=464; cover_image="https://placehold.co/300x450?text=Clean+Code" },
  @{ title="Doraemon - Vol 1"; author="Fujiko F. Fujio"; description="Doraemon manga volume 1 - childhood stories and fun inventions."; price=25000; stock=200; category_name="Thieu nhi"; collection_names=@(); isbn="9786043651270"; publisher="Kim Dong"; published_date="2018-03-01"; pages=192; cover_image="https://placehold.co/300x450?text=Doraemon+1" },

  @{ title="Atomic Habits"; author="James Clear"; description="Tiny habits, remarkable results: get 1% better every day."; price=189000; stock=60; category_name="Ky nang song"; collection_names=@("Best sellers"); isbn="9780735211292"; publisher="Avery"; published_date="2018-10-16"; pages=320; cover_image="https://placehold.co/300x450?text=Atomic+Habits" },
  @{ title="Thinking, Fast and Slow"; author="Daniel Kahneman"; description="Two systems that drive the way we think and make choices."; price=239000; stock=45; category_name="Kinh te"; collection_names=@("New arrivals"); isbn="9786043651287"; publisher="Lao Dong"; published_date="2020-11-20"; pages=640; cover_image="https://placehold.co/300x450?text=Fast+and+Slow" },
  @{ title="Eloquent JavaScript"; author="Marijn Haverbeke"; description="Modern JavaScript with practical examples from basics to advanced."; price=399000; stock=25; category_name="Cong nghe"; collection_names=@("Discount"); isbn="9781593279509"; publisher="No Starch Press"; published_date="2018-12-04"; pages=472; cover_image="https://placehold.co/300x450?text=Eloquent+JS" },
  @{ title="Harry Potter and the Philosopher's Stone"; author="J.K. Rowling"; description="The first book of the famous wizarding series."; price=159000; stock=70; category_name="Van hoc"; collection_names=@("Best sellers"); isbn="9786043651294"; publisher="Tre"; published_date="2017-06-26"; pages=368; cover_image="https://placehold.co/300x450?text=Harry+Potter+1" },
  @{ title="The Story of a Seagull and the Cat Who Taught Her to Fly"; author="Luis Sepulveda"; description="A warm story about love, responsibility, and differences."; price=69000; stock=90; category_name="Thieu nhi"; collection_names=@("New arrivals"); isbn="9786043651300"; publisher="Hoi Nha Van"; published_date="2016-02-12"; pages=144; cover_image="https://placehold.co/300x450?text=Seagull+and+Cat" },

  @{ title="Deep Work"; author="Cal Newport"; description="Focus without distraction to produce high-value work."; price=179000; stock=55; category_name="Ky nang song"; collection_names=@("Discount"); isbn="9781455586691"; publisher="Grand Central"; published_date="2016-01-05"; pages=304; cover_image="https://placehold.co/300x450?text=Deep+Work" },
  @{ title="Refactoring"; author="Martin Fowler"; description="Improving the design of existing code for maintainability and scalability."; price=520000; stock=18; category_name="Cong nghe"; collection_names=@("Best sellers"); isbn="9780134757599"; publisher="Addison-Wesley"; published_date="2018-11-19"; pages=448; cover_image="https://placehold.co/300x450?text=Refactoring" }
)

Write-Host "Creating books (10+ records)..." -ForegroundColor Cyan
$created = 0
foreach ($b in $books) {
  $payload = @{
    title = $b.title
    author = $b.author
    description = $b.description
    price = $b.price
    stock = $b.stock
    category_id = (Get-CategoryId $b.category_name)
    collection_ids = (Get-CollectionIds $b.collection_names)
    isbn = $b.isbn
    publisher = $b.publisher
    published_date = $b.published_date
    pages = $b.pages
    cover_image = $b.cover_image
  }

  $res = Invoke-Json -Method POST -Path "/books/" -Body $payload -Headers $authHeaders
  if ($null -ne $res) { $created++ }
}

Write-Host "=== Done. Created/attempted books: $($books.Count); successful creates: $created ===" -ForegroundColor Green
Write-Host "Open Frontend: http://localhost:3000" -ForegroundColor DarkGray
Write-Host "Open API docs: http://localhost:8000/api/docs/" -ForegroundColor DarkGray
