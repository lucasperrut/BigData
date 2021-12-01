using System;

namespace API.Dtos
{
    public class NewspaperDto
    {
        public DateTime date { get; set; }
        public string hour { get; set; }
        public string text { get; set; }
        public string source { get; set; }
        public string username { get; set; }
        public string hashtags { get; set; }

    }
}