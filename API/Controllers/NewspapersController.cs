using API.Dtos;
using CsvHelper;
using Microsoft.AspNetCore.Mvc;
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;

namespace API.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class NewspapersController : ControllerBase
    {
        [HttpGet]
        public IActionResult Get()
        {
            var files = Directory.GetFiles(Path.GetFullPath($@"{AppDomain.CurrentDomain.BaseDirectory}\CSVs"));

            var records = new List<NewspaperDto>();

            foreach (var file in files)
            {
                using var reader = new StreamReader(file);
                using var csv = new CsvReader(reader, CultureInfo.InvariantCulture);
                var recordsDto = csv.GetRecords<NewspaperDto>();

                records.AddRange(recordsDto);
            }

            return Ok(records);
        }

        [HttpGet("hashtag")]
        public IActionResult GetCountHashtag()
        {
            var files = Directory.GetFiles(Path.GetFullPath($@"{AppDomain.CurrentDomain.BaseDirectory}\CSVs"));

            var records = new List<NewspaperDto>();

            foreach (var file in files)
            {
                using var reader = new StreamReader(file);
                using var csv = new CsvReader(reader, CultureInfo.InvariantCulture);
                var recordsDto = csv.GetRecords<NewspaperDto>();

                records.AddRange(recordsDto);
            }

            var group = records.GroupBy(x => new { x.date, x.hashtags });

            var result = group.Select(x => new
            {
                x.Key.hashtags,
                x.Key.date,
                count = x.Count()
            });

            return Ok(result);
        }

        [HttpGet("words")]
        public IActionResult GetCountWords()
        {
            var files = Directory.GetFiles(Path.GetFullPath($@"{AppDomain.CurrentDomain.BaseDirectory}\CSVs"));

            var records = new List<NewspaperDto>();

            foreach (var file in files)
            {
                using var reader = new StreamReader(file);
                using var csv = new CsvReader(reader, CultureInfo.InvariantCulture);
                var recordsDto = csv.GetRecords<NewspaperDto>();

                records.AddRange(recordsDto);
            }

            var words = new List<string>();
            foreach (var record in records)
            {
                var textSplits = record.text.Split(" ");

                foreach (var textSplit in textSplits)
                {
                    var text = textSplit.Trim().ToUpper();

                    if (text.Length > 3)
                        words.Add(text);
                }
            }

            var group = words.GroupBy(x => x);

            var result = group.Select(x => new
            {
                x.Key,
                count = x.Count()
            });

            return Ok(result);
        }
    }
}