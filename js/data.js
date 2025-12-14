// 最后更新于 2025-12-14
const musicData = [
    {
        "id": 24,
        "title": "Der Feuerreiter/火焰骑士",
        "composer": "Hugo Wolf/沃尔夫",
        "work": "Mörike-Lieder",
        "language": "德语",
        "category": "艺术歌曲",
        "voice_count": "",
        "voice_types": "",
        "tonality": "g小调",
        "filename": "艺术歌曲/Der_Feuerreiter.pdf",
        "date": "2025-12-14"
    },
    {
        "id": 23,
        "title": "Messiah, HWV 56/弥赛亚",
        "composer": "Georg Friedrich Händel/亨德尔",
        "work": "",
        "language": "英语",
        "category": "宗教声乐作品总谱",
        "voice_count": "",
        "voice_types": "SATB独唱与SATB合唱与管弦乐队",
        "tonality": "",
        "filename": "宗教声乐作品总谱/Messiah_HWV_56_Handel.pdf",
        "date": "2025-12-14"
    },
    {
        "id": 22,
        "title": "War Requiem, Op. 66/战争安魂曲",
        "composer": "Benjamin Britten",
        "work": "",
        "language": "拉丁语/英语",
        "category": "宗教声乐作品总谱",
        "voice_count": "",
        "voice_types": "STB独唱与SATB合唱与男童声合唱与管弦乐队及管风琴",
        "tonality": "",
        "filename": "宗教声乐作品总谱/Britten_War_Requiem.pdf",
        "date": "2025-12-14"
    },
    {
        "id": 21,
        "title": "Mass No. 2 in G major, D 167/G大调弥撒",
        "composer": "Franz Schubert/舒伯特",
        "work": "",
        "language": "拉丁语",
        "category": "宗教声乐作品总谱",
        "voice_count": "",
        "voice_types": "STB独唱与SATB合唱与管弦乐队及管风琴",
        "tonality": "G大调",
        "filename": "宗教声乐作品总谱/Schubert_Mass_in_G_Major.pdf",
        "date": "2025-12-13"
    },
    {
        "id": 20,
        "title": "Requiem/安魂曲",
        "composer": "Frederick Delius",
        "work": "",
        "language": "德语",
        "category": "宗教声乐作品总谱",
        "voice_count": "",
        "voice_types": "SB独唱与双合唱队与管弦乐队",
        "tonality": "",
        "filename": "宗教声乐作品总谱/Delius_Requiem.pdf",
        "date": "2025-12-13"
    },
    {
        "id": 19,
        "title": "Requiem, Op. 9/安魂曲",
        "composer": "Maurice Duruflé/杜吕弗莱",
        "work": "",
        "language": "拉丁语",
        "category": "宗教声乐作品总谱",
        "voice_count": "",
        "voice_types": "AB独唱与SATB合唱与管风琴或管弦乐队及管风琴",
        "tonality": "",
        "filename": "宗教声乐作品总谱/Durufle_Requiem.pdf",
        "date": "2025-12-13"
    },
    {
        "id": 17,
        "title": "Requiem in D minor, K. 626/安魂曲",
        "composer": "Wolfgang Amadeus Mozart/莫扎特",
        "work": "",
        "language": "拉丁语",
        "category": "宗教声乐作品总谱",
        "voice_count": "",
        "voice_types": "SATB独唱与SATB合唱与管弦乐队",
        "tonality": "d 小调",
        "filename": "宗教声乐作品总谱/Mozart_Requiem.pdf",
        "date": "2025-12-13"
    },
    {
        "id": 16,
        "title": "Messe de Requiem, Op. 54/安魂曲",
        "composer": "Saint-Saëns/圣桑",
        "work": "",
        "language": "拉丁语",
        "category": "宗教声乐作品总谱",
        "voice_count": "",
        "voice_types": "SATB独唱与SATB合唱与管弦乐队",
        "tonality": "",
        "filename": "宗教声乐作品总谱/Saint-Saens_Requiem.pdf",
        "date": "2025-12-13"
    },
    {
        "id": 15,
        "title": "Requiem in B♭ minor, Op. 89, B. 165/安魂曲",
        "composer": "Antonín Dvořák/德沃夏克",
        "work": "",
        "language": "拉丁语",
        "category": "宗教声乐作品总谱",
        "voice_count": "",
        "voice_types": "SATB独唱与SATB合唱与管弦乐队",
        "tonality": "降b小调",
        "filename": "宗教声乐作品总谱/Dvorak_Requiem.pdf",
        "date": "2025-12-13"
    },
    {
        "id": 14,
        "title": "Requiem in D Minor, Op. 48/安魂曲",
        "composer": "Gabriel Fauré/福雷",
        "work": "",
        "language": "拉丁语",
        "category": "宗教声乐作品总谱",
        "voice_count": "",
        "voice_types": "SB独唱与SATB合唱与管弦乐队和管风琴",
        "tonality": "d 小调",
        "filename": "宗教声乐作品总谱/Faure_Requiem.pdf",
        "date": "2025-12-13"
    },
    {
        "id": 13,
        "title": "Ein deutsches Requiem/德意志安魂曲",
        "composer": "Johannes Brahms/勃拉姆斯",
        "work": "",
        "language": "德语",
        "category": "宗教声乐作品总谱",
        "voice_count": "",
        "voice_types": "SB独唱与SATB合唱与管弦乐队",
        "tonality": "",
        "filename": "宗教声乐作品总谱/Brahms_Requiem.pdf",
        "date": "2025-12-13"
    },
    {
        "id": 12,
        "title": "Cantata BWV 82/Ich habe genug",
        "composer": "J.S. Bach/巴赫",
        "work": "",
        "language": "德语",
        "category": "宗教声乐作品总谱",
        "voice_count": "",
        "voice_types": "",
        "tonality": "",
        "filename": "宗教声乐作品总谱/BWV_82_.pdf",
        "date": "2025-12-13"
    },
    {
        "id": 10,
        "title": "Confrontation",
        "composer": "Claude-Michel Schönberg",
        "work": "Les Misérables/悲惨世界",
        "language": "英语",
        "category": "音乐剧重唱",
        "voice_count": "二重唱",
        "voice_types": "TB",
        "tonality": "",
        "filename": "音乐剧重唱/-_.pdf",
        "date": "2025-12-13"
    },
    {
        "id": 9,
        "title": "Estuans interius",
        "composer": "Carl Orff/奥尔夫",
        "work": "Carmina Burana/布兰诗歌",
        "language": "拉丁语",
        "category": "清唱剧咏叹调",
        "voice_count": "",
        "voice_types": "Baritone/男中音",
        "tonality": "",
        "filename": "清唱剧咏叹调/Estuans_interius-.pdf",
        "date": "2025-12-13"
    },
    {
        "id": 8,
        "title": "Pezzo concertato",
        "composer": "Gioachino Rossini/罗西尼",
        "work": "Il viaggio a Reims/兰斯之旅",
        "language": "意大利语",
        "category": "歌剧重唱",
        "voice_count": "十四重唱/Ensemble",
        "voice_types": "十四重唱/Ensemble",
        "tonality": "",
        "filename": "歌剧重唱/Pezzo_concertato_Il_viaggio_a_Reims.pdf",
        "date": "2025-12-13"
    },
    {
        "id": 7,
        "title": "Pur ti miro",
        "composer": "Claudio Monteverdi/蒙特威尔第",
        "work": "L'incoronazione di Poppea",
        "language": "意大利语",
        "category": "歌剧重唱",
        "voice_count": "二重唱",
        "voice_types": "SA",
        "tonality": "",
        "filename": "歌剧重唱/Duet_Pur_ti_miro_Lincoronazione_di_Poppea.pdf",
        "date": "2025-12-13"
    },
    {
        "id": 6,
        "title": "Bella Figlia Dell' Amore",
        "composer": "Giuseppe Verdi/威尔第",
        "work": "Rigoletto/弄臣",
        "language": "意大利语",
        "category": "歌剧重唱",
        "voice_count": "四重唱",
        "voice_types": "SATB",
        "filename": "歌剧重唱/Rigoletto_Quartet.pdf",
        "date": "2025-12-13",
        "tonality": ""
    },
    {
        "id": 5,
        "title": "The Tempest/暴风雨",
        "composer": "Thomas adès",
        "work": "",
        "language": "英语",
        "category": "歌剧总谱",
        "filename": "歌剧总谱/Thomas_ades_.pdf",
        "date": "2025-12-12"
    },
    {
        "id": 4,
        "title": "When I Fly",
        "composer": "Rachel Portman",
        "work": "The Little Prince",
        "language": "英语",
        "category": "歌剧咏叹调",
        "filename": "歌剧咏叹调/When_I_Fly-_The_Little_Prince.pdf",
        "date": "2025-12-12",
        "voice_count": "",
        "voice_types": "Baritone/男中音",
        "tonality": ""
    },
    {
        "id": 3,
        "title": "Herr Oluf",
        "composer": "Carl Loewe",
        "work": "3 Balladen, Op.2",
        "language": "德语",
        "category": "艺术歌曲",
        "filename": "艺术歌曲/Herr_Oluf_Loewe.pdf",
        "date": "2025-12-12",
        "voice_count": "",
        "voice_types": "",
        "tonality": "e小调"
    },
    {
        "id": 2,
        "title": "A Hundred Thousand Stars",
        "composer": "Jake Heggie",
        "work": "Out of Darkness",
        "language": "英语",
        "category": "歌剧咏叹调",
        "filename": "歌剧咏叹调/A_Hundred_Thousand_Stars-Out_of_Darkness.pdf",
        "date": "2025-12-12",
        "voice_count": "",
        "voice_types": "Baritone/男中音",
        "tonality": ""
    },
    {
        "id": 1,
        "title": "E sogno, O realta?/是梦幻，是现实？",
        "composer": "Giuseppe Verdi/威尔第",
        "work": "Falstaff（法斯塔夫）",
        "language": "意大利语",
        "category": "歌剧咏叹调",
        "filename": "歌剧咏叹调/E_sogno_O_realta-Falstaff.pdf",
        "date": "2025-12-12",
        "voice_count": "",
        "voice_types": "Baritone/男中音",
        "tonality": ""
    }
];
const changeLog = [
    {
        "date": "2025-12-14 00:36",
        "type": "add",
        "msg": "添加了新乐谱：《Der Feuerreiter/火焰骑士》 (Hugo Wolf/沃尔夫)"
    },
    {
        "date": "2025-12-14 00:29",
        "type": "add",
        "msg": "添加了新乐谱：《Messiah, HWV 56/弥赛亚》 (Georg Friedrich Händel/亨德尔)"
    },
    {
        "date": "2025-12-14 00:21",
        "type": "add",
        "msg": "添加了新乐谱：《War Requiem, Op. 66/战争安魂曲》 (Benjamin Britten)"
    },
    {
        "date": "2025-12-13 13:14",
        "type": "delete",
        "msg": "移除了乐谱：《War Requiem, Op. 66/战争安魂曲》 (Benjamin Britten/布里顿)"
    },
    {
        "date": "2025-12-13 13:12",
        "type": "update",
        "msg": "更新了乐谱信息：《Ein deutsches Requiem/德意志安魂曲》"
    },
    {
        "date": "2025-12-13 13:10",
        "type": "add",
        "msg": "添加了新乐谱：《Mass No. 2 in G major, D 167/G大调弥撒》 (Franz Schubert/舒伯特)"
    },
    {
        "date": "2025-12-13 13:07",
        "type": "add",
        "msg": "添加了新乐谱：《Requiem/安魂曲》 (Frederick Delius)"
    },
    {
        "date": "2025-12-13 13:05",
        "type": "update",
        "msg": "更新了乐谱信息：《Requiem in D Minor, Op. 48/安魂曲》"
    },
    {
        "date": "2025-12-13 13:05",
        "type": "update",
        "msg": "更新了乐谱信息：《Requiem in B♭ minor, Op. 89, B. 165/安魂曲》"
    },
    {
        "date": "2025-12-13 13:05",
        "type": "update",
        "msg": "更新了乐谱信息：《Messe de Requiem, Op. 54/安魂曲》"
    },
    {
        "date": "2025-12-13 13:05",
        "type": "update",
        "msg": "更新了乐谱信息：《Requiem in D minor, K. 626/安魂曲》"
    },
    {
        "date": "2025-12-13 13:05",
        "type": "update",
        "msg": "更新了乐谱信息：《War Requiem, Op. 66/战争安魂曲》"
    },
    {
        "date": "2025-12-13 13:05",
        "type": "update",
        "msg": "更新了乐谱信息：《Requiem, Op. 9/安魂曲》"
    },
    {
        "date": "2025-12-13 13:04",
        "type": "add",
        "msg": "添加了新乐谱：《Requiem, Op. 9》 (Maurice Duruflé)"
    },
    {
        "date": "2025-12-13 13:02",
        "type": "add",
        "msg": "添加了新乐谱：《War Requiem, Op. 66/战争安魂曲》 (Benjamin Britten)"
    },
    {
        "date": "2025-12-13 13:00",
        "type": "update",
        "msg": "更新了乐谱信息：《Cantata BWV 82/Ich habe genug》"
    },
    {
        "date": "2025-12-13 12:55",
        "type": "add",
        "msg": "添加了新乐谱：《Requiem in D minor, K. 626/安魂曲》 (Wolfgang Amadeus Mozart)"
    },
    {
        "date": "2025-12-13 12:54",
        "type": "update",
        "msg": "更新了乐谱信息：《Requiem in D Minor, Op. 48/安魂曲》"
    },
    {
        "date": "2025-12-13 12:54",
        "type": "update",
        "msg": "更新了乐谱信息：《Requiem in D Minor, Op. 48/安魂曲》"
    },
    {
        "date": "2025-12-13 12:54",
        "type": "update",
        "msg": "更新了乐谱信息：《Requiem in B♭ minor, Op. 89, B. 165/安魂曲》"
    },
    {
        "date": "2025-12-13 12:53",
        "type": "add",
        "msg": "添加了新乐谱：《Messe de Requiem, Op. 54/安魂曲》 (Saint-Saëns)"
    },
    {
        "date": "2025-12-13 12:52",
        "type": "update",
        "msg": "更新了乐谱信息：《Requiem in B♭ minor, Op. 89, B. 165/安魂曲》"
    },
    {
        "date": "2025-12-13 12:51",
        "type": "update",
        "msg": "更新了乐谱信息：《Requiem in B♭ minor, Op. 89, B. 165》"
    },
    {
        "date": "2025-12-13 12:50",
        "type": "update",
        "msg": "更新了乐谱信息：《Requiem in D Minor, Op. 48/安魂曲》"
    },
    {
        "date": "2025-12-13 12:48",
        "type": "add",
        "msg": "添加了新乐谱：《Requiem in B♭ minor, Op. 89, B. 165》 (Dvořák)"
    },
    {
        "date": "2025-12-13 12:44",
        "type": "add",
        "msg": "添加了新乐谱：《Requiem in D Minor/安魂曲》 (Gabriel Fauré)"
    },
    {
        "date": "2025-12-13 12:22",
        "type": "update",
        "msg": "更新了乐谱信息：《Ein deutsches Requiem/德意志安魂曲》"
    },
    {
        "date": "2025-12-13 12:20",
        "type": "add",
        "msg": "添加了新乐谱：《德意志安魂曲》 (勃拉姆斯)"
    },
    {
        "date": "2025-12-13 12:19",
        "type": "delete",
        "msg": "移除了乐谱：《德意志安魂曲》 (勃拉姆斯)"
    },
    {
        "date": "2025-12-13 12:18",
        "type": "add",
        "msg": "添加了新乐谱：《德意志安魂曲》 (勃拉姆斯)"
    },
    {
        "date": "2025-12-13 12:18",
        "type": "delete",
        "msg": "移除了乐谱：《德意志安魂曲》 (勃拉姆斯)"
    },
    {
        "date": "2025-12-13 12:17",
        "type": "add",
        "msg": "添加了新乐谱：《德意志安魂曲》 (勃拉姆斯)"
    },
    {
        "date": "2025-12-13 12:16",
        "type": "delete",
        "msg": "移除了乐谱：《Ein deutsches Requiem/德意志安魂曲》 (Johannes Brahms/勃拉姆斯)"
    },
    {
        "date": "2025-12-13 11:57",
        "type": "add",
        "msg": "添加了新乐谱：《Cantata BWV 82》 (J.S. Bach/巴赫)"
    },
    {
        "date": "2025-12-13 11:56",
        "type": "add",
        "msg": "添加了新乐谱：《Ein deutsches Requiem/德意志安魂曲》 (Johannes Brahms/勃拉姆斯)"
    },
    {
        "date": "2025-12-13 11:54",
        "type": "add",
        "msg": "添加了新乐谱：《Confrontation》 (Claude-Michel Schönberg)"
    },
    {
        "date": "2025-12-13 11:51",
        "type": "add",
        "msg": "添加了新乐谱：《Estuans interius》 (Carl Orff/奥尔夫)"
    },
    {
        "date": "2025-12-13 09:49",
        "type": "update",
        "msg": "更新了乐谱信息：《Pezzo concertato》"
    },
    {
        "date": "2025-12-13 09:47",
        "type": "add",
        "msg": "添加了新乐谱：《Pezzo concertato》 (Gioachino Rossini/罗西尼)"
    },
    {
        "date": "2025-12-13 09:44",
        "type": "update",
        "msg": "更新了乐谱信息：《E sogno, O realta?/是梦幻，是现实？》"
    },
    {
        "date": "2025-12-13 09:44",
        "type": "update",
        "msg": "更新了乐谱信息：《Bella Figlia Dell' Amore》"
    },
    {
        "date": "2025-12-13 09:44",
        "type": "add",
        "msg": "添加了新乐谱：《Pur ti miro》 (Claudio Monteverdi/蒙特威尔第)"
    }
];
