param(
    [string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot)
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.Drawing

function New-Color([string]$Hex) {
    return [System.Drawing.ColorTranslator]::FromHtml($Hex)
}

function New-Font([float]$Size, [System.Drawing.FontStyle]$Style = [System.Drawing.FontStyle]::Regular) {
    return New-Object System.Drawing.Font('Segoe UI', $Size, $Style)
}

function Draw-WrappedText {
    param(
        [System.Drawing.Graphics]$Graphics,
        [string]$Text,
        [System.Drawing.Font]$Font,
        [System.Drawing.Brush]$Brush,
        [float]$X,
        [float]$Y,
        [float]$Width,
        [float]$Height,
        [System.Drawing.StringAlignment]$Alignment = [System.Drawing.StringAlignment]::Near
    )

    $format = New-Object System.Drawing.StringFormat
    $format.Alignment = $Alignment
    $format.LineAlignment = [System.Drawing.StringAlignment]::Near
    $format.Trimming = [System.Drawing.StringTrimming]::Word
    $format.FormatFlags = [System.Drawing.StringFormatFlags]::LineLimit
    $rect = New-Object System.Drawing.RectangleF($X, $Y, $Width, $Height)
    $Graphics.DrawString($Text, $Font, $Brush, $rect, $format)
    $format.Dispose()
}

function Draw-Arrow {
    param(
        [System.Drawing.Graphics]$Graphics,
        [float]$X1,
        [float]$Y1,
        [float]$X2,
        [float]$Y2,
        [System.Drawing.Color]$Color
    )

    $pen = New-Object System.Drawing.Pen($Color, 3)
    $pen.EndCap = [System.Drawing.Drawing2D.LineCap]::ArrowAnchor
    $Graphics.DrawLine($pen, $X1, $Y1, $X2, $Y2)
    $pen.Dispose()
}

function New-Canvas {
    param(
        [int]$Width,
        [int]$Height,
        [System.Drawing.Color]$Background
    )

    $bitmap = New-Object System.Drawing.Bitmap($Width, $Height)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
    $graphics.Clear($Background)
    return @{ Bitmap = $bitmap; Graphics = $graphics }
}

function Save-Canvas {
    param(
        $Canvas,
        [string]$Path
    )

    $Canvas.Bitmap.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
    $Canvas.Graphics.Dispose()
    $Canvas.Bitmap.Dispose()
}

function Draw-RoundedBox {
    param(
        [System.Drawing.Graphics]$Graphics,
        [float]$X,
        [float]$Y,
        [float]$Width,
        [float]$Height,
        [System.Drawing.Color]$Fill,
        [System.Drawing.Color]$Border,
        [string]$Title,
        [string]$Body
    )

    $rect = New-Object System.Drawing.RectangleF($X, $Y, $Width, $Height)
    $path = New-Object System.Drawing.Drawing2D.GraphicsPath
    $radius = 18.0
    $diameter = $radius * 2
    $path.AddArc($X, $Y, $diameter, $diameter, 180, 90)
    $path.AddArc($X + $Width - $diameter, $Y, $diameter, $diameter, 270, 90)
    $path.AddArc($X + $Width - $diameter, $Y + $Height - $diameter, $diameter, $diameter, 0, 90)
    $path.AddArc($X, $Y + $Height - $diameter, $diameter, $diameter, 90, 90)
    $path.CloseFigure()

    $fillBrush = New-Object System.Drawing.SolidBrush($Fill)
    $borderPen = New-Object System.Drawing.Pen($Border, 2)
    $titleBrush = New-Object System.Drawing.SolidBrush((New-Color '#0F172A'))
    $bodyBrush = New-Object System.Drawing.SolidBrush((New-Color '#334155'))

    $Graphics.FillPath($fillBrush, $path)
    $Graphics.DrawPath($borderPen, $path)
    Draw-WrappedText -Graphics $Graphics -Text $Title -Font (New-Font 14 ([System.Drawing.FontStyle]::Bold)) -Brush $titleBrush -X ($X + 16) -Y ($Y + 14) -Width ($Width - 32) -Height 24
    Draw-WrappedText -Graphics $Graphics -Text $Body -Font (New-Font 10.5) -Brush $bodyBrush -X ($X + 16) -Y ($Y + 42) -Width ($Width - 32) -Height ($Height - 48)

    $fillBrush.Dispose()
    $borderPen.Dispose()
    $titleBrush.Dispose()
    $bodyBrush.Dispose()
    $path.Dispose()
}

function Generate-BusinessFlow {
    param([string]$OutputPath)

    $canvas = New-Canvas -Width 1800 -Height 1200 -Background (New-Color '#F8FAFC')
    $g = $canvas.Graphics

    $titleBrush = New-Object System.Drawing.SolidBrush((New-Color '#0F172A'))
    $subtitleBrush = New-Object System.Drawing.SolidBrush((New-Color '#475569'))
    Draw-WrappedText -Graphics $g -Text 'BUSINESS FLOW - HRM + QUAN LY TAI SAN + KE TOAN' -Font (New-Font 28 ([System.Drawing.FontStyle]::Bold)) -Brush $titleBrush -X 60 -Y 30 -Width 1680 -Height 50
    Draw-WrappedText -Graphics $g -Text 'Happy path end-to-end for Odoo 15: HRM is the master data source; assets are allocated by employee and department; depreciation is posted automatically into the general ledger.' -Font (New-Font 14) -Brush $subtitleBrush -X 60 -Y 82 -Width 1680 -Height 40

    $laneNames = @('Nhan vien/Quan ly', 'HR', 'Quan ly tai san', 'Ke toan/Tai chinh', 'He thong Odoo')
    $laneColors = @('#FDE68A', '#BFDBFE', '#BBF7D0', '#FBCFE8', '#DDD6FE')
    $laneTop = 150
    $laneHeight = 180
    for ($i = 0; $i -lt $laneNames.Count; $i++) {
        $y = $laneTop + ($i * 190)
        $brush = New-Object System.Drawing.SolidBrush((New-Color $laneColors[$i]))
        $pen = New-Object System.Drawing.Pen((New-Color '#CBD5E1'), 1)
        $g.FillRectangle($brush, 40, $y, 1720, $laneHeight)
        $g.DrawRectangle($pen, 40, $y, 1720, $laneHeight)
        Draw-WrappedText -Graphics $g -Text $laneNames[$i] -Font (New-Font 15 ([System.Drawing.FontStyle]::Bold)) -Brush $titleBrush -X 55 -Y ($y + 12) -Width 250 -Height 30
        $brush.Dispose()
        $pen.Dispose()
    }

    $steps = @(
        @{ X = 280; Y = 185; W = 250; H = 105; Fill = '#FEF3C7'; Border = '#F59E0B'; Title = '1. Asset request'; Body = 'Employee or manager submits a request to purchase or assign an asset for work.' },
        @{ X = 560; Y = 375; W = 270; H = 110; Fill = '#DBEAFE'; Border = '#3B82F6'; Title = '2. HR master data'; Body = 'HR updates employee, department and job history. These records remain the master data for the workflow.' },
        @{ X = 860; Y = 565; W = 275; H = 118; Fill = '#DCFCE7'; Border = '#22C55E'; Title = '3. Create asset profile'; Body = 'Asset team creates the asset code, category, original value, depreciation method and start date.' },
        @{ X = 1165; Y = 565; W = 275; H = 118; Fill = '#DCFCE7'; Border = '#22C55E'; Title = '4. Allocate to employee'; Body = 'System validates the HR department and auto closes any previous active allocation of the same asset.' },
        @{ X = 1425; Y = 945; W = 285; H = 118; Fill = '#EDE9FE'; Border = '#8B5CF6'; Title = '5. Monthly automation'; Body = 'An Odoo cron checks due assets every month and creates one depreciation history record per due period.' },
        @{ X = 1165; Y = 755; W = 275; H = 118; Fill = '#FCE7F3'; Border = '#EC4899'; Title = '6. Post ledger entry'; Body = 'Accounting receives the journal entry automatically: debit depreciation expense, credit accumulated depreciation.' },
        @{ X = 860; Y = 945; W = 275; H = 118; Fill = '#EDE9FE'; Border = '#8B5CF6'; Title = '7. Update asset value'; Body = 'Current value, depreciation history and next depreciation date are updated consistently in the asset record.' },
        @{ X = 560; Y = 755; W = 270; H = 110; Fill = '#FCE7F3'; Border = '#EC4899'; Title = '8. Finance reporting'; Body = 'Finance tracks depreciation expense, accumulated depreciation and budget impact for future purchases.' },
        @{ X = 260; Y = 185 + 190; W = 270; H = 110; Fill = '#DBEAFE'; Border = '#3B82F6'; Title = '9. HR transfer update'; Body = 'When HR changes an employee department, the system auto revokes active allocations that no longer match HR master data.' }
    )

    foreach ($step in $steps) {
        Draw-RoundedBox -Graphics $g -X $step.X -Y $step.Y -Width $step.W -Height $step.H -Fill (New-Color $step.Fill) -Border (New-Color $step.Border) -Title $step.Title -Body $step.Body
    }

    Draw-Arrow -Graphics $g -X1 535 -Y1 235 -X2 560 -Y2 425 -Color (New-Color '#475569')
    Draw-Arrow -Graphics $g -X1 815 -Y1 425 -X2 850 -Y2 620 -Color (New-Color '#475569')
    Draw-Arrow -Graphics $g -X1 1110 -Y1 620 -X2 1140 -Y2 620 -Color (New-Color '#475569')
    Draw-Arrow -Graphics $g -X1 1400 -Y1 675 -X2 1450 -Y2 945 -Color (New-Color '#475569')
    Draw-Arrow -Graphics $g -X1 1430 -Y1 995 -X2 1400 -Y2 810 -Color (New-Color '#475569')
    Draw-Arrow -Graphics $g -X1 1140 -Y1 810 -X2 1110 -Y2 995 -Color (New-Color '#475569')
    Draw-Arrow -Graphics $g -X1 850 -Y1 995 -X2 815 -Y2 810 -Color (New-Color '#475569')
    Draw-Arrow -Graphics $g -X1 535 -Y1 425 -X2 535 -Y2 235 -Color (New-Color '#94A3B8')

    $noteBrush = New-Object System.Drawing.SolidBrush((New-Color '#334155'))
    Draw-WrappedText -Graphics $g -Text 'Required integration point: HRM provides employee and department master data; the asset module reuses that data directly; accounting receives the depreciation entry automatically. Level-2 triggers include monthly depreciation, auto reallocation closure and HR transfer revocation.' -Font (New-Font 12) -Brush $noteBrush -X 60 -Y 1090 -Width 1680 -Height 50
    $titleBrush.Dispose()
    $subtitleBrush.Dispose()
    $noteBrush.Dispose()

    Save-Canvas -Canvas $canvas -Path $OutputPath
}

function Generate-Poster {
    param([string]$OutputPath)

    $canvas = New-Canvas -Width 1600 -Height 2000 -Background (New-Color '#FFFDF8')
    $g = $canvas.Graphics
    $navy = New-Color '#0F172A'
    $teal = New-Color '#0F766E'
    $orange = New-Color '#EA580C'
    $sand = New-Color '#FDE68A'

    $headerBrush = New-Object System.Drawing.SolidBrush($navy)
    $accentBrush = New-Object System.Drawing.SolidBrush($orange)
    $mutedBrush = New-Object System.Drawing.SolidBrush((New-Color '#475569'))
    $whiteBrush = New-Object System.Drawing.SolidBrush((New-Color '#FFFFFF'))

    $g.FillRectangle((New-Object System.Drawing.SolidBrush((New-Color '#FFF7ED'))), 0, 0, 1600, 330)
    $g.FillEllipse((New-Object System.Drawing.SolidBrush((New-Color '#FED7AA'))), 1080, -80, 460, 460)
    $g.FillEllipse((New-Object System.Drawing.SolidBrush((New-Color '#CCFBF1'))), -120, 90, 380, 380)

    Draw-WrappedText -Graphics $g -Text 'HE THONG QUAN LY TAI SAN - KE TOAN - HRM' -Font (New-Font 36 ([System.Drawing.FontStyle]::Bold)) -Brush $headerBrush -X 70 -Y 80 -Width 980 -Height 90
    Draw-WrappedText -Graphics $g -Text 'Built on Odoo 15 to manage assets, monthly depreciation, general ledger posting and HR master-data synchronization on one shared database.' -Font (New-Font 17) -Brush $mutedBrush -X 75 -Y 180 -Width 980 -Height 80

    Draw-RoundedBox -Graphics $g -X 70 -Y 380 -Width 460 -Height 230 -Fill (New-Color '#CCFBF1') -Border $teal -Title '1. HRM as master data' -Body 'The nhan_su module manages employees, departments, roles and job history. Asset allocation always reuses these records.'
    Draw-RoundedBox -Graphics $g -X 570 -Y 380 -Width 460 -Height 230 -Fill (New-Color '#FFEDD5') -Border $orange -Title '2. Centralized asset control' -Body 'quan_ly_tai_san tracks original value, current value, depreciation settings, active department and active employee.'
    Draw-RoundedBox -Graphics $g -X 1070 -Y 380 -Width 460 -Height 230 -Fill (New-Color '#E0E7FF') -Border (New-Color '#6366F1') -Title '3. Auto depreciation and GL' -Body 'Each due period creates depreciation history and the accounting entry automatically. Event triggers also close obsolete allocations.'

    Draw-WrappedText -Graphics $g -Text 'Gia tri noi bat' -Font (New-Font 24 ([System.Drawing.FontStyle]::Bold)) -Brush $headerBrush -X 70 -Y 670 -Width 400 -Height 40
    $featureLines = @(
        'No duplicate employee data entry across modules',
        'Asset control by department and employee',
        'Monthly depreciation runs automatically by configuration',
        'Reallocation and HR transfer triggers close invalid allocations',
        'General ledger is updated as soon as depreciation is posted',
        'Supports cost reporting and purchase-budget planning'
    )
    for ($i = 0; $i -lt $featureLines.Count; $i++) {
        $y = 735 + ($i * 70)
        $g.FillEllipse($accentBrush, 80, $y + 10, 18, 18)
        Draw-WrappedText -Graphics $g -Text $featureLines[$i] -Font (New-Font 18) -Brush $mutedBrush -X 115 -Y $y -Width 1250 -Height 35
    }

    $g.FillRectangle((New-Object System.Drawing.SolidBrush($navy)), 70, 1110, 1460, 360)
    Draw-WrappedText -Graphics $g -Text 'Kich ban van hanh' -Font (New-Font 26 ([System.Drawing.FontStyle]::Bold)) -Brush $whiteBrush -X 110 -Y 1150 -Width 400 -Height 50
    Draw-WrappedText -Graphics $g -Text '1. HR creates employees and departments.' -Font (New-Font 17) -Brush $whiteBrush -X 110 -Y 1235 -Width 500 -Height 30
    Draw-WrappedText -Graphics $g -Text '2. Asset team registers the asset and depreciation settings.' -Font (New-Font 17) -Brush $whiteBrush -X 110 -Y 1280 -Width 700 -Height 30
    Draw-WrappedText -Graphics $g -Text '3. Asset allocation reuses HR data and closes the previous active allocation automatically.' -Font (New-Font 17) -Brush $whiteBrush -X 110 -Y 1325 -Width 980 -Height 30
    Draw-WrappedText -Graphics $g -Text '4. Odoo creates depreciation history and the accounting entry on schedule.' -Font (New-Font 17) -Brush $whiteBrush -X 110 -Y 1370 -Width 820 -Height 30
    Draw-WrappedText -Graphics $g -Text '5. HR transfer events automatically revoke invalid allocations; finance tracks remaining value for budgeting.' -Font (New-Font 17) -Brush $whiteBrush -X 110 -Y 1415 -Width 1150 -Height 40

    Draw-RoundedBox -Graphics $g -X 70 -Y 1540 -Width 700 -Height 280 -Fill (New-Color '#FEF3C7') -Border (New-Color '#D97706') -Title 'Cong nghe va kien truc' -Body 'Platform: Python Odoo 15. Integrated modules: nhan_su + quan_ly_tai_san + account. All modules share one database and a scheduled depreciation cron reduces manual work.'
    Draw-RoundedBox -Graphics $g -X 830 -Y 1540 -Width 700 -Height 280 -Fill (New-Color '#DCFCE7') -Border (New-Color '#16A34A') -Title 'Huong mo rong muc 3' -Body 'This solution can be extended with AI OCR for asset invoices, an internal policy chatbot, or Telegram/Zalo alerts when assets require approval, reassignment or maintenance.'

    Draw-WrappedText -Graphics $g -Text 'BTL hoi nhap quan tri - Odoo 15 submission kit' -Font (New-Font 16 ([System.Drawing.FontStyle]::Bold)) -Brush $headerBrush -X 70 -Y 1900 -Width 600 -Height 30
    Draw-WrappedText -Graphics $g -Text 'Generated from scripts/generate_submission_assets.ps1 for GitHub submission packaging.' -Font (New-Font 14) -Brush $mutedBrush -X 70 -Y 1935 -Width 900 -Height 30

    $headerBrush.Dispose()
    $accentBrush.Dispose()
    $mutedBrush.Dispose()
    $whiteBrush.Dispose()

    Save-Canvas -Canvas $canvas -Path $OutputPath
}

$businessFlowPath = Join-Path $ProjectRoot 'docs/business flow/NhomXX_BusinessFlow_QuanLyTaiSanKeToanHRM.png'
$posterPath = Join-Path $ProjectRoot 'docs/poster/NhomXX_Poster_QuanLyTaiSanKeToanHRM.png'

Generate-BusinessFlow -OutputPath $businessFlowPath
Generate-Poster -OutputPath $posterPath

Write-Host "Generated: $businessFlowPath"
Write-Host "Generated: $posterPath"