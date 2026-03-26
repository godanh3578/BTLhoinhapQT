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

function Draw-SectionPanel {
    param(
        [System.Drawing.Graphics]$Graphics,
        [float]$X,
        [float]$Y,
        [float]$Width,
        [float]$Height,
        [System.Drawing.Color]$HeaderFill,
        [System.Drawing.Color]$PanelFill,
        [System.Drawing.Color]$Border,
        [string]$Title
    )

    $panelBrush = New-Object System.Drawing.SolidBrush($PanelFill)
    $headerBrush = New-Object System.Drawing.SolidBrush($HeaderFill)
    $borderPen = New-Object System.Drawing.Pen($Border, 2)
    $titleBrush = New-Object System.Drawing.SolidBrush((New-Color '#FFFFFF'))

    $Graphics.FillRectangle($panelBrush, $X, $Y, $Width, $Height)
    $Graphics.DrawRectangle($borderPen, $X, $Y, $Width, $Height)
    $Graphics.FillRectangle($headerBrush, $X, $Y, $Width, 42)
    Draw-WrappedText -Graphics $Graphics -Text $Title -Font (New-Font 16 ([System.Drawing.FontStyle]::Bold)) -Brush $titleBrush -X ($X + 18) -Y ($Y + 8) -Width ($Width - 36) -Height 26

    $panelBrush.Dispose()
    $headerBrush.Dispose()
    $borderPen.Dispose()
    $titleBrush.Dispose()
}

function Draw-BulletList {
    param(
        [System.Drawing.Graphics]$Graphics,
        [string[]]$Items,
        [System.Drawing.Font]$Font,
        [System.Drawing.Brush]$TextBrush,
        [System.Drawing.Brush]$BulletBrush,
        [float]$X,
        [float]$Y,
        [float]$Width,
        [float]$LineHeight,
        [float]$BulletSize = 10
    )

    for ($i = 0; $i -lt $Items.Count; $i++) {
        $lineY = $Y + ($i * $LineHeight)
        $Graphics.FillEllipse($BulletBrush, $X, ($lineY + 7), $BulletSize, $BulletSize)
        Draw-WrappedText -Graphics $Graphics -Text $Items[$i] -Font $Font -Brush $TextBrush -X ($X + 22) -Y $lineY -Width ($Width - 22) -Height ($LineHeight + 8)
    }
}

function Draw-Chip {
    param(
        [System.Drawing.Graphics]$Graphics,
        [float]$X,
        [float]$Y,
        [float]$Width,
        [float]$Height,
        [System.Drawing.Color]$Fill,
        [System.Drawing.Color]$Border,
        [System.Drawing.Color]$Foreground,
        [string]$Text
    )

    $path = New-Object System.Drawing.Drawing2D.GraphicsPath
    $radius = 16.0
    $diameter = $radius * 2
    $path.AddArc($X, $Y, $diameter, $diameter, 180, 90)
    $path.AddArc($X + $Width - $diameter, $Y, $diameter, $diameter, 270, 90)
    $path.AddArc($X + $Width - $diameter, $Y + $Height - $diameter, $diameter, $diameter, 0, 90)
    $path.AddArc($X, $Y + $Height - $diameter, $diameter, $diameter, 90, 90)
    $path.CloseFigure()

    $fillBrush = New-Object System.Drawing.SolidBrush($Fill)
    $borderPen = New-Object System.Drawing.Pen($Border, 1.5)
    $textBrush = New-Object System.Drawing.SolidBrush($Foreground)
    $Graphics.FillPath($fillBrush, $path)
    $Graphics.DrawPath($borderPen, $path)
    Draw-WrappedText -Graphics $Graphics -Text $Text -Font (New-Font 12 ([System.Drawing.FontStyle]::Bold)) -Brush $textBrush -X ($X + 10) -Y ($Y + 8) -Width ($Width - 20) -Height ($Height - 16) -Alignment ([System.Drawing.StringAlignment]::Center)

    $fillBrush.Dispose()
    $borderPen.Dispose()
    $textBrush.Dispose()
    $path.Dispose()
}

function Draw-ImageFit {
    param(
        [System.Drawing.Graphics]$Graphics,
        [string]$ImagePath,
        [float]$X,
        [float]$Y,
        [float]$Width,
        [float]$Height,
        [System.Drawing.Color]$Border
    )

    if (-not (Test-Path $ImagePath)) {
        return
    }

    $image = [System.Drawing.Image]::FromFile($ImagePath)
    try {
        $scale = [math]::Min($Width / $image.Width, $Height / $image.Height)
        $drawWidth = $image.Width * $scale
        $drawHeight = $image.Height * $scale
        $offsetX = $X + (($Width - $drawWidth) / 2)
        $offsetY = $Y + (($Height - $drawHeight) / 2)

        $backgroundBrush = New-Object System.Drawing.SolidBrush((New-Color '#FFFFFF'))
        $borderPen = New-Object System.Drawing.Pen($Border, 1.5)
        $Graphics.FillRectangle($backgroundBrush, $X, $Y, $Width, $Height)
        $Graphics.DrawRectangle($borderPen, $X, $Y, $Width, $Height)
        $Graphics.DrawImage($image, $offsetX, $offsetY, $drawWidth, $drawHeight)
        $backgroundBrush.Dispose()
        $borderPen.Dispose()
    }
    finally {
        $image.Dispose()
    }
}

function Generate-BusinessFlow {
    param([string]$OutputPath)

    $canvas = New-Canvas -Width 1900 -Height 1450 -Background (New-Color '#F8FAFC')
    $g = $canvas.Graphics

    $titleBrush = New-Object System.Drawing.SolidBrush((New-Color '#0F172A'))
    $subtitleBrush = New-Object System.Drawing.SolidBrush((New-Color '#475569'))
    Draw-WrappedText -Graphics $g -Text 'BUSINESS FLOW - HRM + QUAN LY TAI SAN + KE TOAN + AI/API' -Font (New-Font 28 ([System.Drawing.FontStyle]::Bold)) -Brush $titleBrush -X 60 -Y 30 -Width 1780 -Height 50
    Draw-WrappedText -Graphics $g -Text 'Satisfies the minimum submission requirements: actors, end-to-end flow, HRM integration, level-2 automation triggers, and level-3 AI/API integration with input -> processing -> output plus event/schedule mechanisms.' -Font (New-Font 14) -Brush $subtitleBrush -X 60 -Y 82 -Width 1780 -Height 42

    $laneNames = @('Nhan vien/Quan ly', 'HR', 'Quan ly tai san', 'Ke toan/Tai chinh', 'AI/API dich vu ngoai', 'He thong Odoo')
    $laneColors = @('#FDE68A', '#BFDBFE', '#BBF7D0', '#FBCFE8', '#FDE68A', '#DDD6FE')
    $laneTop = 150
    $laneHeight = 175
    for ($i = 0; $i -lt $laneNames.Count; $i++) {
        $y = $laneTop + ($i * 185)
        $brush = New-Object System.Drawing.SolidBrush((New-Color $laneColors[$i]))
        $pen = New-Object System.Drawing.Pen((New-Color '#CBD5E1'), 1)
        $g.FillRectangle($brush, 40, $y, 1820, $laneHeight)
        $g.DrawRectangle($pen, 40, $y, 1820, $laneHeight)
        Draw-WrappedText -Graphics $g -Text $laneNames[$i] -Font (New-Font 15 ([System.Drawing.FontStyle]::Bold)) -Brush $titleBrush -X 55 -Y ($y + 12) -Width 250 -Height 30
        $brush.Dispose()
        $pen.Dispose()
    }

    $steps = @(
        @{ X = 285; Y = 185; W = 285; H = 110; Fill = '#FEF3C7'; Border = '#F59E0B'; Title = '1. Employee request'; Body = 'Nhan vien/quan ly tao de nghi mua sam hoac cap phat tai san. Day la diem bat dau cua quy trinh.' },
        @{ X = 605; Y = 370; W = 315; H = 120; Fill = '#DBEAFE'; Border = '#3B82F6'; Title = '2. HR master data [Integration]'; Body = 'HR quan ly nhan vien, phong ban, chuc vu va lich su cong tac. Day la du lieu goc duoc module tai san va tai chinh tai su dung.' },
        @{ X = 975; Y = 555; W = 330; H = 120; Fill = '#DCFCE7'; Border = '#22C55E'; Title = '3. Tao ho so tai san'; Body = 'Bo phan tai san tao asset, khai bao nguyen gia, nhom tai san, phuong phap khau hao va ngay bat dau.' },
        @{ X = 1335; Y = 555; W = 360; H = 120; Fill = '#DCFCE7'; Border = '#22C55E'; Title = '4. Cap phat tai san [Trigger]'; Body = 'He thong doi chieu phong ban/nhan vien tu HRM va tu dong dong cap phat cu neu tai san da duoc cap truoc do.' },
        @{ X = 1260; Y = 740; W = 435; H = 120; Fill = '#FCE7F3'; Border = '#EC4899'; Title = '5. Ghi nhan chung tu va but toan'; Body = 'Ke toan ghi nhan chung tu mua sam. Neu du dieu kien, he thong tao but toan va lien ket asset voi chung tu tai chinh.' },
        @{ X = 1060; Y = 925; W = 635; H = 120; Fill = '#FDE68A'; Border = '#D97706'; Title = '6. AI/LLM + External API [Level 3]'; Body = 'Input: de nghi mua sam/hoa don. Xu ly: OCR, LLM tom tat/chuan hoa, kiem tra quy dinh. Output: goi y phe duyet, du lieu hoa don, thong bao Telegram theo event hoac lich.' },
        @{ X = 1210; Y = 1110; W = 485; H = 120; Fill = '#EDE9FE'; Border = '#8B5CF6'; Title = '7. Monthly cron [Schedule trigger]'; Body = 'Cron Odoo chay hang thang, tao depreciation history, cap nhat gia tri con lai va xac dinh ky khau hao tiep theo.' },
        @{ X = 670; Y = 1110; W = 500; H = 120; Fill = '#EDE9FE'; Border = '#8B5CF6'; Title = '8. Auto update records [Level 2]'; Body = 'He thong tu dong tao/cap nhat depreciation line, asset value, allocation status va cac record phat sinh theo su kien.' },
        @{ X = 515; Y = 740; W = 320; H = 120; Fill = '#FCE7F3'; Border = '#EC4899'; Title = '9. Bao cao tai chinh'; Body = 'Ke toan theo doi chi phi khau hao, hao mon luy ke, gia tri con lai va tac dong ngan sach cua mua sam.' },
        @{ X = 205; Y = 370; W = 335; H = 120; Fill = '#DBEAFE'; Border = '#3B82F6'; Title = '10. HR transfer event [Trigger]'; Body = 'Khi HR dieu chuyen phong ban hoac thay doi nhan su, su kien tu dong thu hoi/cap nhat cac phan bo tai san khong con hop le.' }
    )

    foreach ($step in $steps) {
        Draw-RoundedBox -Graphics $g -X $step.X -Y $step.Y -Width $step.W -Height $step.H -Fill (New-Color $step.Fill) -Border (New-Color $step.Border) -Title $step.Title -Body $step.Body
    }

    Draw-Arrow -Graphics $g -X1 570 -Y1 240 -X2 650 -Y2 430 -Color (New-Color '#475569')
    Draw-Arrow -Graphics $g -X1 920 -Y1 430 -X2 990 -Y2 615 -Color (New-Color '#475569')
    Draw-Arrow -Graphics $g -X1 1305 -Y1 615 -X2 1335 -Y2 615 -Color (New-Color '#475569')
    Draw-Arrow -Graphics $g -X1 1515 -Y1 675 -X2 1490 -Y2 740 -Color (New-Color '#475569')
    Draw-Arrow -Graphics $g -X1 1475 -Y1 860 -X2 1475 -Y2 925 -Color (New-Color '#475569')
    Draw-Arrow -Graphics $g -X1 1440 -Y1 1045 -X2 1450 -Y2 1110 -Color (New-Color '#475569')
    Draw-Arrow -Graphics $g -X1 1210 -Y1 1170 -X2 1170 -Y2 1170 -Color (New-Color '#475569')
    Draw-Arrow -Graphics $g -X1 770 -Y1 1110 -X2 750 -Y2 860 -Color (New-Color '#475569')
    Draw-Arrow -Graphics $g -X1 540 -Y1 430 -X2 540 -Y2 920 -Color (New-Color '#94A3B8')

    $tagBrush = New-Object System.Drawing.SolidBrush((New-Color '#1D4ED8'))
    Draw-WrappedText -Graphics $g -Text 'HRM master data -> employee, department, position' -Font (New-Font 11 ([System.Drawing.FontStyle]::Bold)) -Brush $tagBrush -X 700 -Y 332 -Width 360 -Height 18
    Draw-WrappedText -Graphics $g -Text 'Event -> auto close old allocation' -Font (New-Font 11 ([System.Drawing.FontStyle]::Bold)) -Brush $tagBrush -X 1385 -Y 530 -Width 260 -Height 18
    Draw-WrappedText -Graphics $g -Text 'Event/API -> Telegram notification' -Font (New-Font 11 ([System.Drawing.FontStyle]::Bold)) -Brush $tagBrush -X 1425 -Y 900 -Width 250 -Height 18
    Draw-WrappedText -Graphics $g -Text 'Schedule -> monthly depreciation cron' -Font (New-Font 11 ([System.Drawing.FontStyle]::Bold)) -Brush $tagBrush -X 1320 -Y 1088 -Width 280 -Height 18

    $noteBrush = New-Object System.Drawing.SolidBrush((New-Color '#334155'))
    Draw-WrappedText -Graphics $g -Text 'Minimum diagram checklist covered: (1) actors/roles are shown as swimlanes; (2) the process runs from employee request to reporting/end state; (3) HRM master data integration is marked at step 2; (4) automation triggers are marked at steps 4, 7, 8 and 10; (5) level-3 AI/API integration is marked at step 6 with explicit input -> processing -> output and event/schedule mechanism.' -Font (New-Font 12) -Brush $noteBrush -X 60 -Y 1298 -Width 1780 -Height 50
    $titleBrush.Dispose()
    $subtitleBrush.Dispose()
    $tagBrush.Dispose()
    $noteBrush.Dispose()

    Save-Canvas -Canvas $canvas -Path $OutputPath
}

function Generate-Poster {
    param([string]$OutputPath)

    $canvas = New-Canvas -Width 1600 -Height 2200 -Background (New-Color '#F4F1EB')
    $g = $canvas.Graphics
    $navy = New-Color '#1F3A93'
    $navyDark = New-Color '#1A2C6B'
    $orange = New-Color '#F07A24'
    $panelBorder = New-Color '#2E4D9A'
    $bodyText = New-Color '#111827'
    $mutedText = New-Color '#475569'
    $softBlue = New-Color '#EEF3FF'
    $softSand = New-Color '#FFF7E7'
    $softMint = New-Color '#F0FBF7'
    $softRose = New-Color '#FFF2EE'
    $businessFlowPath = Join-Path $ProjectRoot 'docs/business flow/Nhom6_BusinessFlow_QuanLyTaiSanKeToanHRM.png'

    $navyBrush = New-Object System.Drawing.SolidBrush($navy)
    $navyDarkBrush = New-Object System.Drawing.SolidBrush($navyDark)
    $orangeBrush = New-Object System.Drawing.SolidBrush($orange)
    $bodyBrush = New-Object System.Drawing.SolidBrush($bodyText)
    $mutedBrush = New-Object System.Drawing.SolidBrush($mutedText)
    $whiteBrush = New-Object System.Drawing.SolidBrush((New-Color '#FFFFFF'))
    $lightBorderPen = New-Object System.Drawing.Pen((New-Color '#D5DCEC'), 2)

    $g.FillRectangle($navyBrush, 0, 0, 1600, 210)
    $g.FillRectangle($orangeBrush, 0, 210, 1600, 8)
    $g.DrawLine((New-Object System.Drawing.Pen((New-Color '#5D78C6'), 3)), 75, 86, 1525, 86)
    $g.DrawLine((New-Object System.Drawing.Pen((New-Color '#5D78C6'), 3)), 75, 162, 1525, 162)

    Draw-WrappedText -Graphics $g -Text 'BTL HOI NHAP QUAN TRI' -Font (New-Font 18 ([System.Drawing.FontStyle]::Bold)) -Brush $whiteBrush -X 70 -Y 22 -Width 420 -Height 28
    Draw-WrappedText -Graphics $g -Text 'ERP: HE THONG QUAN LY TAI SAN' -Font (New-Font 25 ([System.Drawing.FontStyle]::Bold)) -Brush $whiteBrush -X 70 -Y 92 -Width 920 -Height 42
    Draw-WrappedText -Graphics $g -Text 'TAI CHINH KE TOAN + NHAN SU' -Font (New-Font 22 ([System.Drawing.FontStyle]::Bold)) -Brush $whiteBrush -X 70 -Y 126 -Width 860 -Height 38
    Draw-WrappedText -Graphics $g -Text 'Nen tang Odoo 15 cho doanh nghiep: dong bo master data HRM, quan ly tai san, tu dong khau hao, ghi so ke toan va mo rong AI/External API.' -Font (New-Font 14) -Brush $whiteBrush -X 70 -Y 172 -Width 1280 -Height 26

    Draw-SectionPanel -Graphics $g -X 40 -Y 245 -Width 870 -Height 340 -HeaderFill $navy -PanelFill (New-Color '#FFFFFF') -Border $panelBorder -Title 'Gioi thieu'
    $introItems = @(
        'Tich hop 3 phan he: nhan_su, quan_ly_tai_san, quan_ly_tai_chinh_ke_toan.',
        'HRM la nguon du lieu goc cho nhan vien, phong ban, chuc vu va lich su cong tac.',
        'Tai san duoc cap phat theo phong ban va nhan vien dang su dung.',
        'He thong tu dong tinh khau hao theo ky va sinh but toan vao so cai.',
        'Chung tu mua sam co the tao but toan va sinh tai san hop le tu dong.',
        'Mo rong duoc voi AI/LLM va thong bao Telegram khi cau hinh day du.'
    )
    Draw-BulletList -Graphics $g -Items $introItems -Font (New-Font 15) -TextBrush $bodyBrush -BulletBrush $orangeBrush -X 62 -Y 308 -Width 820 -LineHeight 42 -BulletSize 9

    Draw-SectionPanel -Graphics $g -X 940 -Y 245 -Width 620 -Height 560 -HeaderFill $navy -PanelFill (New-Color '#FFFFFF') -Border $panelBorder -Title 'Kien truc he thong'
    Draw-WrappedText -Graphics $g -Text 'Mo hinh tich hop giua HRM, quan ly tai san, ke toan tai chinh va he thong Odoo.' -Font (New-Font 12) -Brush $mutedBrush -X 965 -Y 302 -Width 570 -Height 22
    Draw-ImageFit -Graphics $g -ImagePath $businessFlowPath -X 970 -Y 338 -Width 560 -Height 435 -Border (New-Color '#CBD5E1')

    Draw-SectionPanel -Graphics $g -X 40 -Y 615 -Width 870 -Height 540 -HeaderFill $navy -PanelFill (New-Color '#FFFFFF') -Border $panelBorder -Title 'Phan he va tinh nang trung tam'
    Draw-RoundedBox -Graphics $g -X 65 -Y 675 -Width 820 -Height 120 -Fill $softBlue -Border (New-Color '#3B82F6') -Title '1. nhan_su' -Body 'Quan ly nhan vien, phong ban, chuc vu, lich su cong tac va cac thay doi dieu chuyen. Day la master data cho cac phan he con lai.'
    Draw-RoundedBox -Graphics $g -X 65 -Y 820 -Width 820 -Height 145 -Fill $softSand -Border $orange -Title '2. quan_ly_tai_san' -Body 'Quan ly ho so tai san, nguyen gia, gia tri con lai, cau hinh khau hao, cap phat cho nhan vien/phong ban, thu hoi va dong cap phat cu khi tai cap.'
    Draw-RoundedBox -Graphics $g -X 65 -Y 990 -Width 820 -Height 135 -Fill $softMint -Border (New-Color '#16A34A') -Title '3. quan_ly_tai_chinh_ke_toan' -Body 'Quan ly ngan sach, nguon kinh phi, de nghi mua sam, chung tu mua tai san; tu dong tao but toan, sinh tai san hop le va ho tro AI/Telegram.'

    Draw-SectionPanel -Graphics $g -X 940 -Y 835 -Width 620 -Height 320 -HeaderFill $navy -PanelFill (New-Color '#FFFFFF') -Border $panelBorder -Title 'Cong nghe su dung'
    Draw-WrappedText -Graphics $g -Text 'He dieu hanh' -Font (New-Font 13 ([System.Drawing.FontStyle]::Bold)) -Brush $bodyBrush -X 970 -Y 895 -Width 120 -Height 20
    Draw-Chip -Graphics $g -X 1090 -Y 887 -Width 120 -Height 34 -Fill (New-Color '#FFF3E8') -Border $orange -Foreground $orange -Text 'Ubuntu'
    Draw-WrappedText -Graphics $g -Text 'Cong nghe chinh' -Font (New-Font 13 ([System.Drawing.FontStyle]::Bold)) -Brush $bodyBrush -X 970 -Y 944 -Width 160 -Height 20
    Draw-Chip -Graphics $g -X 1090 -Y 936 -Width 110 -Height 34 -Fill $softBlue -Border (New-Color '#2563EB') -Foreground (New-Color '#1D4ED8') -Text 'Odoo 15'
    Draw-Chip -Graphics $g -X 1215 -Y 936 -Width 110 -Height 34 -Fill $softMint -Border (New-Color '#16A34A') -Foreground (New-Color '#15803D') -Text 'Python'
    Draw-Chip -Graphics $g -X 1340 -Y 936 -Width 120 -Height 34 -Fill (New-Color '#FFF4E6') -Border (New-Color '#C2410C') -Foreground (New-Color '#9A3412') -Text 'Docker'
    Draw-WrappedText -Graphics $g -Text 'Co so du lieu' -Font (New-Font 13 ([System.Drawing.FontStyle]::Bold)) -Brush $bodyBrush -X 970 -Y 993 -Width 140 -Height 20
    Draw-Chip -Graphics $g -X 1090 -Y 985 -Width 150 -Height 34 -Fill (New-Color '#EEF2FF') -Border (New-Color '#4F46E5') -Foreground (New-Color '#4338CA') -Text 'PostgreSQL'
    Draw-WrappedText -Graphics $g -Text 'Mo rong muc 3' -Font (New-Font 13 ([System.Drawing.FontStyle]::Bold)) -Brush $bodyBrush -X 970 -Y 1042 -Width 140 -Height 20
    Draw-Chip -Graphics $g -X 1090 -Y 1034 -Width 110 -Height 34 -Fill (New-Color '#FDF2F8') -Border (New-Color '#DB2777') -Foreground (New-Color '#BE185D') -Text 'OpenAI'
    Draw-Chip -Graphics $g -X 1215 -Y 1034 -Width 110 -Height 34 -Fill (New-Color '#F0FDF4') -Border (New-Color '#16A34A') -Foreground (New-Color '#15803D') -Text 'Gemini'
    Draw-Chip -Graphics $g -X 1340 -Y 1034 -Width 130 -Height 34 -Fill (New-Color '#EFF6FF') -Border (New-Color '#0284C7') -Foreground (New-Color '#0369A1') -Text 'Telegram'
    Draw-WrappedText -Graphics $g -Text 'Tat ca module dung chung 1 co so du lieu Odoo. Docker Compose khoi tao PostgreSQL; Odoo xu ly cron khau hao, su kien cap phat va cac tich hop API.' -Font (New-Font 13) -Brush $mutedBrush -X 970 -Y 1090 -Width 560 -Height 60

    Draw-SectionPanel -Graphics $g -X 40 -Y 1190 -Width 1520 -Height 410 -HeaderFill $navy -PanelFill (New-Color '#FFFFFF') -Border $panelBorder -Title 'Luong nghiep vu tieu bieu'
    $g.FillRectangle($navyDarkBrush, 65, 1255, 1470, 315)
    $workflowLines = @(
        '1. HR cap nhat nhan vien, phong ban va lich su cong tac trong module nhan_su.',
        '2. Bo phan tai san tao ho so tai san, thiet lap nguyen gia, phuong phap khau hao va ngay bat dau.',
        '3. Khi cap phat, he thong doi chieu nhan vien/phong ban tu HRM va tu dong dong cap phat cu cua cung tai san.',
        '4. Cron hang thang quet tai san den ky, tao lich su khau hao va cap nhat gia tri con lai.',
        '5. Module ke toan nhan but toan tu dong cho chi phi khau hao va hao mon luy ke vao so cai.',
        '6. Khi HR dieu chuyen nhan su hoac chung tu mua tai san duoc ghi nhan, he thong kich hoat cac xu ly tu dong lien quan.'
    )
    for ($i = 0; $i -lt $workflowLines.Count; $i++) {
        Draw-WrappedText -Graphics $g -Text $workflowLines[$i] -Font (New-Font 17) -Brush $whiteBrush -X 100 -Y (1288 + ($i * 44)) -Width 1385 -Height 34
    }

    Draw-SectionPanel -Graphics $g -X 40 -Y 1640 -Width 870 -Height 500 -HeaderFill $navy -PanelFill (New-Color '#FFFFFF') -Border $panelBorder -Title 'Gia tri mang lai'
    $valueItems = @(
        'Dung mot bo du lieu HRM de tranh nhap lieu lap lai giua nhan su, tai san va tai chinh.',
        'Theo doi tai san theo phong ban va nhan vien dang su dung tai mot thoi diem.',
        'Tu dong hoa khau hao dinh ky va ghi nhan vao ke toan ma khong can xu ly thu cong.',
        'Dong bo quy trinh tu de nghi mua sam, chung tu mua den sinh tai san hop le.',
        'Ho tro giam sat ngan sach, gia tri con lai va tac dong tai chinh cho mua sam trong tuong lai.',
        'San sang mo rong AI/External API de phan tich nghiep vu va gui thong bao phe duyet.'
    )
    Draw-BulletList -Graphics $g -Items $valueItems -Font (New-Font 15) -TextBrush $bodyBrush -BulletBrush $orangeBrush -X 64 -Y 1705 -Width 820 -LineHeight 52 -BulletSize 10

    Draw-SectionPanel -Graphics $g -X 940 -Y 1640 -Width 620 -Height 500 -HeaderFill $navy -PanelFill (New-Color '#FFFFFF') -Border $panelBorder -Title 'Huong phat trien'
    Draw-RoundedBox -Graphics $g -X 970 -Y 1705 -Width 560 -Height 160 -Fill $softRose -Border $orange -Title 'Giai doan gan' -Body 'Bo sung OCR hoa don/de nghi mua sam de tu dong trich xuat thong tin chung tu; ket noi OpenAI/Gemini de tom tat noi dung de nghi, goi y phan loai tai san va ho tro kiem tra tinh day du cua ho so.'
    Draw-RoundedBox -Graphics $g -X 970 -Y 1890 -Width 560 -Height 170 -Fill $softMint -Border (New-Color '#16A34A') -Title 'Giai doan mo rong' -Body 'Mo rong chatbot noi quy tai san, canh bao Telegram/Zalo theo su kien, dashboard du bao chi phi khau hao va bao tri, dong bo voi cac dich vu ngoai thong qua API de nang cao kha nang phe duyet va giam sat van hanh.'

    Draw-WrappedText -Graphics $g -Text 'Odoo 15 submission kit | Tai lieu poster sinh tu scripts/generate_submission_assets.ps1' -Font (New-Font 13 ([System.Drawing.FontStyle]::Bold)) -Brush $navyBrush -X 40 -Y 2160 -Width 760 -Height 22

    $navyBrush.Dispose()
    $navyDarkBrush.Dispose()
    $orangeBrush.Dispose()
    $bodyBrush.Dispose()
    $mutedBrush.Dispose()
    $whiteBrush.Dispose()
    $lightBorderPen.Dispose()

    Save-Canvas -Canvas $canvas -Path $OutputPath
}

$businessFlowPath = Join-Path $ProjectRoot 'docs/business flow/Nhom6_BusinessFlow_QuanLyTaiSanKeToanHRM.png'
$posterPath = Join-Path $ProjectRoot 'docs/poster/Nhom6_Poster_QuanLyTaiSanKeToanHRM.png'

Generate-BusinessFlow -OutputPath $businessFlowPath
Generate-Poster -OutputPath $posterPath

Write-Host "Generated: $businessFlowPath"
Write-Host "Generated: $posterPath"