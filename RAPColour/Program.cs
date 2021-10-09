using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using System.Text.RegularExpressions;

namespace RAPColour
{
    class Program
    {
        static Color innardCol = Color.FromArgb(128, 128, 0, 0),
                     borderCol = Color.FromArgb(255, 255, 0, 0);

        static Int64 quality = 90L;
        static string outFolder = "./output/";
        static string[] fileFormats = { "jpg", "jpeg", "png", "gif", "webp", "bmp", "exif", "tiff" };

        private static void Main(string[] args)
        {
            string filename = args[0].Trim();

            String regexStr = "[a-z0-9]{1,}.(?:" + String.Join("|", fileFormats) + "){1}";
            Regex regex = new Regex(regexStr, RegexOptions.IgnoreCase);

            MatchCollection matches = regex.Matches(filename);

            if (matches[0].Value != filename)
            {
                Console.WriteLine("Please ensure the image is one of the following file formats:");
                Console.WriteLine(String.Join(", ", fileFormats));
                Console.WriteLine("and ensure the executable is called in the same format as below:");
                Console.WriteLine("\"./RAPColour.exe file.png\"");
                Console.ReadLine();
                return;
            }

            Bitmap sourceImg = new Bitmap(filename),
                   overlay = new Bitmap(sourceImg.Width, sourceImg.Height);

            int[] start = { Int32.Parse(args[1]), Int32.Parse(args[2]) };

            // get colour of first selected pixel
            Color sourceColor = sourceImg.GetPixel(start[0], start[1]);
            int[] sourceRGB = { sourceColor.R, sourceColor.G, sourceColor.B };

            Queue<int[]> pixelQueue = new Queue<int[]>();
            pixelQueue.Enqueue(start);

            // 2d searched array to skip already traversed pixels
            byte[,] searched = new byte[sourceImg.Width, sourceImg.Height];
            generateSearchMap(searched);
            searched[start[0], start[1]] = 1;

            long startTime = ((DateTimeOffset)DateTime.Now).ToUnixTimeMilliseconds();

            // while there's a pixel in queue, check it
            while (pixelQueue.Count > 0)
            {
                int[] coords = pixelQueue.Dequeue();

                // checks the 4 adjacent pixels
                bool top = checkAdjPixel(sourceImg, sourceRGB, coords, 0, -1, pixelQueue, searched),
                     right = checkAdjPixel(sourceImg, sourceRGB, coords, 1, 0, pixelQueue, searched),
                     bottom = checkAdjPixel(sourceImg, sourceRGB, coords, 0, 1, pixelQueue, searched),
                     left = checkAdjPixel(sourceImg, sourceRGB, coords, -1, 0, pixelQueue, searched);

                // determines whether the pixel is a "border" pixel (an adjacent pixel is not of similar colour)
                Color fillCol = (top || right || bottom || left) ? borderCol : innardCol;
                overlay.SetPixel(coords[0], coords[1], fillCol);
            }

            long endTime = ((DateTimeOffset)DateTime.Now).ToUnixTimeMilliseconds();
            long diff = endTime - startTime;
            Console.WriteLine("Process took {0} ms long", diff);

            // naming and saving overlay image
            string[] spl = filename.Split(".");
            spl[0] += "_overlay_" + endTime;
            overlay.Save(outFolder + String.Join(".", spl));

            // naming and saving merged image
            Bitmap merged = MergedBitmaps(overlay, sourceImg);
            spl = filename.Split(".");
            spl[0] += "_merged_" + ((DateTimeOffset)DateTime.Now).ToUnixTimeMilliseconds();
            spl[1] = "jpg";

            // compresses image before saving, will be in jpg format
            ImageCodecInfo pngEncoder = GetEncoder(ImageFormat.Jpeg);
            Encoder myEncoder = Encoder.Quality;

            EncoderParameters myEncoderParams = new EncoderParameters(1);
            myEncoderParams.Param[0] = new EncoderParameter(myEncoder, quality);
            merged.Save(outFolder + String.Join(".", spl), pngEncoder, myEncoderParams);
        }

        // merges bmp1 above bmp2
        private static Bitmap MergedBitmaps(Bitmap bmp1, Bitmap bmp2)
        {
            Bitmap result = new Bitmap(Math.Max(bmp1.Width, bmp2.Width),
                                       Math.Max(bmp1.Height, bmp2.Height));
            using (Graphics g = Graphics.FromImage(result))
            {
                g.DrawImage(bmp2, Point.Empty);
                g.DrawImage(bmp1, Point.Empty);
            }

            return result;
        }

        // returns image codec specified
        private static ImageCodecInfo GetEncoder(ImageFormat format)
        {
            foreach (ImageCodecInfo codec in ImageCodecInfo.GetImageEncoders())
            {
                if (codec.FormatID == format.Guid)
                    return codec;
            }
            return null;
        }

        // checks if adjacent pixel is already searched / in queue
        private static bool checkAdjPixel(Bitmap sourceImg, int[] sourceRGB, int[] source, int shiftX, int shiftY, Queue<int[]> pixelQueue, byte[,] searched)
        {
            // ensures coordinates are not out of bounds
            bool boundaryCheck = (source[0] > 0 &&
                                  source[0] < sourceImg.Width - 1 &&
                                  source[1] > 0 &&
                                  source[1] < sourceImg.Height - 1);
            if (boundaryCheck)
            {
                int[] adjCoords = { source[0] + shiftX, source[1] + shiftY };

                if (searched[adjCoords[0], adjCoords[1]] == 0)
                {
                    Color adjCol = sourceImg.GetPixel(adjCoords[0], adjCoords[1]);
                    if (checkRGBVar(sourceRGB, adjCol.R, adjCol.G, adjCol.B))
                    {
                        searched[adjCoords[0], adjCoords[1]] = 1;
                        pixelQueue.Enqueue(adjCoords);
                    }
                    // if adjacent colour doesn't match, current pixel is a boundary
                    else
                        return true;
                }
            }
            return false;
        }

        // populates 2d search array with 0's, 1 being searched
        private static void generateSearchMap(byte[,] searched)
        {
            for (int i = 0; i < searched.GetLength(0); i++)
            {
                for (int j = 0; j < searched.GetLength(1); j++)
                {
                    searched[i, j] = 0;
                }
            }
        }

        // checks if values of R, G and B are at least 80% similar
        private static bool checkRGBVar(int[] sourceRGB, int R, int G, int B)
        {
            float rDiff = 255 - Math.Abs((sourceRGB[0] - R)),
                  gDiff = 255 - Math.Abs((sourceRGB[1] - G)),
                  bDiff = 255 - Math.Abs((sourceRGB[2] - B));

            rDiff /= 255;
            gDiff /= 255;
            bDiff /= 255;

            return ((rDiff + gDiff + bDiff) / 3 >= 0.80);
        }
    }
}
